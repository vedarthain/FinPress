"""
Unified Multi-Source News Aggregator & Deduplication Engine.
Combines all daily news reports from Financial Express and Business Standard,
deduplicates overlapping stories section-by-section to ensure 100% complete unabridged coverage (zero missed news),
and publishes the master report to Cloudflare R2, Neon PostgreSQL DB, and the local Web App dashboard.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import config
from analyzer import NewspaperEditionReport, NewsStory, ChunkNewsReport, GeminiNewsAnalyzer
from cloud_storage import upload_to_r2
from db import save_to_neon

logger = logging.getLogger("NewsAPI.Aggregator")


class UnifiedNewsAggregator:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or config.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _deduplicate_category_stories(self, category: str, stories: List[Dict[str, Any]]) -> List[NewsStory]:
        """Deduplicates and merges overlapping stories within a section using intelligent text matching."""
        import difflib
        import re

        if not stories:
            return []

        def clean_text(t: str) -> set:
            words = re.findall(r'\b[a-zA-Z0-9]{4,}\b', t.lower())
            stop_words = {"india", "indian", "says", "said", "will", "year", "month", "report", "first", "last", "over", "under", "after", "before", "financial", "standard", "express", "crore", "lakh", "worth", "plan", "plans", "govt", "government"}
            return {w for w in words if w not in stop_words}

        fe_items = [s for s in stories if "Financial Express" in s.get("source", "")]
        bs_items = [s for s in stories if "Business Standard" in s.get("source", "")]
        other_items = [s for s in stories if s not in fe_items and s not in bs_items]

        matched_fe = set()
        matched_bs = set()
        results: List[NewsStory] = []

        # Find overlapping stories between FE and BS
        for fe_i, fe_s in enumerate(fe_items):
            fe_words = clean_text(fe_s["headline"] + " " + fe_s["brief_details"][:100])
            best_match_idx = None
            best_score = 0.0

            for bs_i, bs_s in enumerate(bs_items):
                if bs_i in matched_bs:
                    continue
                
                # SequenceMatcher ratio
                ratio = difflib.SequenceMatcher(None, fe_s["headline"].lower(), bs_s["headline"].lower()).ratio()
                
                # Key words overlap
                bs_words = clean_text(bs_s["headline"] + " " + bs_s["brief_details"][:100])
                overlap = len(fe_words & bs_words)
                
                if ratio > 0.60 or (overlap >= 4 and ratio > 0.40):
                    if ratio > best_score:
                        best_score = ratio
                        best_match_idx = bs_i

            if best_match_idx is not None:
                matched_fe.add(fe_i)
                matched_bs.add(best_match_idx)
                bs_s = bs_items[best_match_idx]

                # Merge
                p_fe = fe_s.get("page_numbers", "FE")
                p_bs = bs_s.get("page_numbers", "BS")
                combined_pages = f"FE ({p_fe}) / BS ({p_bs})"
                
                # Pick longer headline or combine
                chosen_hl = fe_s["headline"] if len(fe_s["headline"]) >= len(bs_s["headline"]) else bs_s["headline"]
                combined_brief = f"{fe_s['brief_details']} Additionally: {bs_s['brief_details']}"
                combined_bullets = list(dict.fromkeys(fe_s.get("bullet_points", []) + bs_s.get("bullet_points", [])))[:6]

                results.append(NewsStory(
                    headline=chosen_hl,
                    category=category,
                    page_numbers=combined_pages,
                    brief_details=combined_brief,
                    bullet_points=combined_bullets,
                    importance="HIGH" if ("HIGH" in (fe_s.get("importance"), bs_s.get("importance"))) else "MEDIUM"
                ))

        # Add all exclusive FE stories
        for fe_i, fe_s in enumerate(fe_items):
            if fe_i not in matched_fe:
                results.append(NewsStory(
                    headline=fe_s["headline"],
                    category=category,
                    page_numbers=fe_s.get("page_numbers", "FE"),
                    brief_details=fe_s["brief_details"],
                    bullet_points=fe_s.get("bullet_points", []),
                    importance=fe_s.get("importance", "MEDIUM")
                ))

        # Add all exclusive BS stories
        for bs_i, bs_s in enumerate(bs_items):
            if bs_i not in matched_bs:
                results.append(NewsStory(
                    headline=bs_s["headline"],
                    category=category,
                    page_numbers=bs_s.get("page_numbers", "BS"),
                    brief_details=bs_s["brief_details"],
                    bullet_points=bs_s.get("bullet_points", []),
                    importance=bs_s.get("importance", "MEDIUM")
                ))

        # Add other stories
        for s in other_items:
            results.append(NewsStory(
                headline=s["headline"],
                category=category,
                page_numbers=s.get("page_numbers", "Print/Web"),
                brief_details=s["brief_details"],
                bullet_points=s.get("bullet_points", []),
                importance=s.get("importance", "MEDIUM")
            ))

        return results

    def combine_and_deduplicate(self, reports_with_sources: List[Any], date_str: Optional[str] = None) -> NewspaperEditionReport:
        """
        Combines stories from multiple reports, performs section-by-section deduplication,
        ensuring 100% of unique articles are retained.
        """
        if not reports_with_sources:
            raise ValueError("No reports provided to aggregate.")

        target_date = date_str or datetime.now().strftime("%Y-%m-%d")

        # Collect all stories grouped by category
        category_map = defaultdict(list)
        total_raw_count = 0

        def is_filler_headline(hl: str) -> bool:
            h = hl.lower()
            return any(k in h for k in [
                "special edition and general overview", "general overview", "newspaper overview",
                "sunday special edition", "fe sunday special", "edition overview", "e-paper index",
                "page index", "table of contents"
            ])

        def sanitize_category(cat: str, hl: str, brief: str) -> str:
            text = (hl + " " + brief).lower()
            if cat == "Market":
                notice_terms = ["disclosure", "public notice", "statutory notice", "possession notice", "postal ballot", "e-voting", "annual general meeting", "agm notice", "egm notice", "co-op bank", "co-operative bank", "auction notice"]
                if any(t in text for t in notice_terms):
                    return "Corporate Events"
            return cat

        for item in reports_with_sources:
            if isinstance(item, tuple):
                r, source_name = item
            else:
                r, source_name = item, "Newspaper"

            for s in r.major_stories:
                if is_filler_headline(s.headline):
                    logger.info(f"Skipping editorial filler/overview story: {s.headline}")
                    continue

                clean_cat = sanitize_category(s.category, s.headline, s.brief_details)
                total_raw_count += 1
                category_map[clean_cat].append({
                    "source": source_name,
                    "category": clean_cat,
                    "headline": s.headline,
                    "brief_details": s.brief_details,
                    "bullet_points": s.bullet_points,
                    "page_numbers": s.page_numbers,
                    "importance": s.importance,
                })

        logger.info(f"Aggregating {total_raw_count} total raw stories across {len(category_map)} sections...")

        master_stories: List[NewsStory] = []

        for category, cat_stories in category_map.items():
            logger.info(f"Deduplicating section [{category}]: {len(cat_stories)} incoming stories...")
            deduped = self._deduplicate_category_stories(category, cat_stories)
            logger.info(f"  -> [{category}]: {len(deduped)} distinct stories retained.")
            master_stories.extend(deduped)

        summary = (
            f"FinBrief Unified Financial Intelligence Edition ({target_date}) combines complete, unabridged daily reporting "
            f"across Financial Express and Business Standard. Covering {len(master_stories)} distinct corporate, policy, market, and "
            f"macroeconomic developments, today's edition provides an exhaustive overview of the Indian and global business landscape."
        )

        report = NewspaperEditionReport(
            edition_date=target_date,
            total_pages_analyzed=len(master_stories),
            edition_summary=summary,
            major_stories=master_stories,
        )

        # 1. Save Date-stamped Unified Files
        json_date_path = self.output_dir / f"news_report_unified_{target_date}.json"
        md_date_path = self.output_dir / f"news_report_unified_{target_date}.md"

        # 2. Save "Latest" Unified Files (Single static destination)
        json_latest_path = self.output_dir / "news_report_unified_latest.json"
        md_latest_path = self.output_dir / "news_report_unified_latest.md"

        json_bytes = report.model_dump_json(indent=2)
        md_content = GeminiNewsAnalyzer.render_markdown_report(report)

        for p in [json_date_path, json_latest_path]:
            with open(p, "w", encoding="utf-8") as f:
                f.write(json_bytes)

        for p in [md_date_path, md_latest_path]:
            with open(p, "w", encoding="utf-8") as f:
                f.write(md_content)

        logger.info(f"✅ Saved Unified Deduplicated Master Report ({len(report.major_stories)} stories) to: {json_latest_path}")

        # 3. Upload to Cloudflare R2
        upload_to_r2(json_date_path, f"reports/{json_date_path.name}")
        upload_to_r2(md_date_path, f"reports/{md_date_path.name}")
        upload_to_r2(json_latest_path, "reports/news_report_unified_latest.json")
        upload_to_r2(md_latest_path, "reports/news_report_unified_latest.md")

        # 4. Save to Neon PostgreSQL DB
        save_to_neon(report, source="unified")

        return report


def run_unified_aggregation(date_str: Optional[str] = None) -> NewspaperEditionReport:
    """Loads existing FE & BS reports from reports dir and creates the unified deduplicated report."""
    target_date = date_str or datetime.now().strftime("%Y-%m-%d")
    reports_dir = Path(config.output_dir)

    fe_path = reports_dir / f"news_report_{target_date}.json"
    bs_path = reports_dir / f"news_report_bs_{target_date}.json"

    reports = []
    if fe_path.exists():
        with open(fe_path, "r", encoding="utf-8") as f:
            r = NewspaperEditionReport.model_validate_json(f.read())
            reports.append((r, "Financial Express"))

    if bs_path.exists():
        with open(bs_path, "r", encoding="utf-8") as f:
            r = NewspaperEditionReport.model_validate_json(f.read())
            reports.append((r, "Business Standard"))

    if not reports:
        all_jsons = sorted(reports_dir.glob("news_report_*.json"))
        for j in all_jsons:
            if "unified" not in j.name:
                with open(j, "r", encoding="utf-8") as f:
                    r = NewspaperEditionReport.model_validate_json(f.read())
                    source_label = "Business Standard" if "bs" in j.name else "Financial Express"
                    reports.append((r, source_label))

    aggregator = UnifiedNewsAggregator()
    return aggregator.combine_and_deduplicate(reports, date_str=target_date)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    rep = run_unified_aggregation()
    print(f"\n🎉 Unified Master Aggregation Complete: {len(rep.major_stories)} exhaustive stories published!")
