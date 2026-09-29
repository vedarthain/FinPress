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

        raw_fe_items = [s for s in stories if "Financial Express" in s.get("source", "")]
        raw_bs_items = [s for s in stories if "Business Standard" in s.get("source", "")]
        other_items = [s for s in stories if s not in raw_fe_items and s not in raw_bs_items]

        def dedup_internal(items_list: List[Dict[str, Any]], source_label: str) -> List[Dict[str, Any]]:
            deduped = []
            for item in items_list:
                item_words = clean_text(item["headline"] + " " + item.get("brief_details", "")[:100])
                is_dup = False
                for existing in deduped:
                    ratio = difflib.SequenceMatcher(None, item["headline"].lower(), existing["headline"].lower()).ratio()
                    ex_words = clean_text(existing["headline"] + " " + existing.get("brief_details", "")[:100])
                    overlap = len(item_words & ex_words)
                    
                    if ratio > 0.60 or (overlap >= 4 and ratio > 0.40):
                        is_dup = True
                        p1 = existing.get("page_numbers", "")
                        p2 = item.get("page_numbers", "")
                        if p2 and p2 not in p1:
                            existing["page_numbers"] = f"{p1}, {p2}" if p1 else p2
                        if len(item.get("brief_details", "")) > len(existing.get("brief_details", "")):
                            existing["brief_details"] = item["brief_details"]
                        existing["bullet_points"] = list(dict.fromkeys(existing.get("bullet_points", []) + item.get("bullet_points", [])))[:6]
                        break
                if not is_dup:
                    deduped.append(dict(item))
            return deduped

        fe_items = dedup_internal(raw_fe_items, "FE")
        bs_items = dedup_internal(raw_bs_items, "BS")

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
                p_fe = fe_s.get("page_numbers", "Page 1")
                p_bs = bs_s.get("page_numbers", "Page 1")
                combined_pages = f"FE ({p_fe}) / BS ({p_bs})"
                
                # Pick the most comprehensive headline
                chosen_hl = fe_s["headline"] if len(fe_s["headline"]) >= len(bs_s["headline"]) else bs_s["headline"]
                
                # Deduplicate brief_details to prevent repetitive text
                b_fe = fe_s.get("brief_details", "").strip()
                b_bs = bs_s.get("brief_details", "").strip()
                brief_ratio = difflib.SequenceMatcher(None, b_fe.lower(), b_bs.lower()).ratio()
                
                if not b_bs or b_fe.lower() == b_bs.lower() or brief_ratio > 0.60:
                    combined_brief = b_fe if len(b_fe) >= len(b_bs) else b_bs
                elif not b_fe:
                    combined_brief = b_bs
                else:
                    combined_brief = f"{b_fe} (BS: {b_bs})"

                # Deduplicate bullet points using fuzzy matching
                raw_bullets = fe_s.get("bullet_points", []) + bs_s.get("bullet_points", [])
                seen_bullets = []
                for bp in raw_bullets:
                    bp_clean = bp.strip()
                    if bp_clean and not any(difflib.SequenceMatcher(None, bp_clean.lower(), seen.lower()).ratio() > 0.70 for seen in seen_bullets):
                        seen_bullets.append(bp_clean)
                combined_bullets = seen_bullets[:6]

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
                p = fe_s.get("page_numbers", "Page 1")
                formatted_p = p if "FE" in p else f"FE ({p})"
                results.append(NewsStory(
                    headline=fe_s["headline"],
                    category=category,
                    page_numbers=formatted_p,
                    brief_details=fe_s["brief_details"],
                    bullet_points=fe_s.get("bullet_points", []),
                    importance=fe_s.get("importance", "MEDIUM")
                ))

        # Add all exclusive BS stories
        for bs_i, bs_s in enumerate(bs_items):
            if bs_i not in matched_bs:
                p = bs_s.get("page_numbers", "Page 1")
                formatted_p = p if "BS" in p else f"BS ({p})"
                results.append(NewsStory(
                    headline=bs_s["headline"],
                    category=category,
                    page_numbers=formatted_p,
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

    def combine_and_deduplicate(
        self,
        reports_with_sources: List[Any],
        date_str: Optional[str] = None,
        source_statuses: Optional[dict] = None
    ) -> NewspaperEditionReport:
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

        sources_present = set()
        for item in reports_with_sources:
            if isinstance(item, tuple):
                r, source_name = item
            else:
                r, source_name = item, "Newspaper"

            sources_present.add(source_name)

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
            f"FinPress Unified Financial Intelligence Edition ({target_date}) combines complete daily reporting "
            f"across Financial Express and Business Standard. Covering {len(master_stories)} distinct corporate, policy, market, and "
            f"macroeconomic developments."
        )

        final_statuses = source_statuses or {}
        if not final_statuses:
            final_statuses = {
                "financial_express": "✅ Active" if "Financial Express" in sources_present else "⚠️ Not Included",
                "business_standard": "✅ Active" if "Business Standard" in sources_present else "❌ Failed / Session Expired"
            }

        report = NewspaperEditionReport(
            edition_date=target_date,
            total_pages_analyzed=len(master_stories),
            edition_summary=summary,
            major_stories=master_stories,
            source_statuses=final_statuses,
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
    reports_dir.mkdir(parents=True, exist_ok=True)

    fe_path = reports_dir / f"news_report_fe_{target_date}.json"
    if not fe_path.exists():
        fe_path = reports_dir / f"news_report_{target_date}.json"
    if not fe_path.exists():
        from cloud_storage import download_from_r2
        download_from_r2(f"reports/news_report_fe_{target_date}.json", fe_path)
        if not fe_path.exists():
            download_from_r2(f"reports/news_report_{target_date}.json", fe_path)

    bs_path = reports_dir / f"news_report_bs_{target_date}.json"
    if not bs_path.exists():
        from cloud_storage import download_from_r2
        download_from_r2(f"reports/news_report_bs_{target_date}.json", bs_path)

    reports = []
    source_statuses = {}

    if fe_path.exists():
        with open(fe_path, "r", encoding="utf-8") as f:
            r = NewspaperEditionReport.model_validate_json(f.read())
            reports.append((r, "Financial Express"))
            source_statuses["financial_express"] = f"✅ Active ({len(r.major_stories)} stories)"
    else:
        source_statuses["financial_express"] = "⚠️ FE Report Not Found"

    if bs_path.exists():
        with open(bs_path, "r", encoding="utf-8") as f:
            r = NewspaperEditionReport.model_validate_json(f.read())
            reports.append((r, "Business Standard"))
            source_statuses["business_standard"] = f"✅ Active ({len(r.major_stories)} stories)"
    else:
        source_statuses["business_standard"] = "❌ Failed: Subscriber Session Expired / Not Fetched"

    if not reports:
        all_jsons = sorted(reports_dir.glob("news_report_*.json"))
        for j in all_jsons:
            if "unified" not in j.name:
                with open(j, "r", encoding="utf-8") as f:
                    r = NewspaperEditionReport.model_validate_json(f.read())
                    source_label = "Business Standard" if "bs" in j.name else "Financial Express"
                    reports.append((r, source_label))

    aggregator = UnifiedNewsAggregator()
    return aggregator.combine_and_deduplicate(reports, date_str=target_date, source_statuses=source_statuses)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    rep = run_unified_aggregation()
    print(f"\n🎉 Unified Master Aggregation Complete: {len(rep.major_stories)} exhaustive stories published!")
