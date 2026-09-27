"""
Business Standard Exhaustive News Extractor & Reporter Module.
Fetches all daily print & edition articles across all major business desks (Economy, Policy, Markets, IPO, Companies, Finance, International)
and bifurcates them into the strict 10 categories via Gemini Flash, uploading to Cloudflare R2 and Neon DB.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET

import requests

from config import config
from analyzer import NewspaperEditionReport, NewsStory
from cloud_storage import upload_to_r2
from db import save_to_neon

logger = logging.getLogger("NewsAPI.BSDownloader")

BS_FEEDS = {
    "Economy & Policy": "https://www.business-standard.com/rss/economy-policy-101.rss",
    "Markets & IPO": "https://www.business-standard.com/rss/markets-106.rss",
    "Companies & Corporate": "https://www.business-standard.com/rss/companies-104.rss",
    "Finance": "https://www.business-standard.com/rss/finance-103.rss",
    "Industry & Sectors": "https://www.business-standard.com/rss/industry-105.rss",
    "International": "https://www.business-standard.com/rss/international-188.rss",
}


class BusinessStandardFetcher:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or config.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*"
        }

    def fetch_all_raw_articles(self) -> List[Dict[str, str]]:
        """Extracts all raw articles across all Business Standard desks."""
        raw_stories = []
        seen_titles = set()

        for desk, feed_url in BS_FEEDS.items():
            try:
                resp = requests.get(feed_url, headers=self.headers, timeout=15)
                if resp.status_code != 200:
                    logger.warning(f"Feed {desk} returned status {resp.status_code}")
                    continue

                root = ET.fromstring(resp.content)
                items = root.findall(".//item")
                logger.info(f"Retrieved {len(items)} articles from Business Standard [{desk}]")

                for it in items:
                    title_elem = it.find("title")
                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                    if not title or title.lower() in seen_titles:
                        continue

                    seen_titles.add(title.lower())
                    desc_elem = it.find("description")
                    desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
                    link_elem = it.find("link")
                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                    pub_elem = it.find("pubDate")
                    pub = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""

                    raw_stories.append({
                        "desk": desk,
                        "title": title,
                        "description": desc,
                        "link": link,
                        "pubDate": pub,
                    })

            except Exception as e:
                logger.error(f"Error fetching Business Standard feed {desk}: {e}")

        logger.info(f"Total unique Business Standard articles fetched: {len(raw_stories)}")
        return raw_stories

    def analyze_and_bifurcate(self, raw_stories: List[Dict[str, str]]) -> NewspaperEditionReport:
        """Sends all raw articles in batches to Gemini Flash to classify and bifurcate every single story."""
        from google import genai
        from google.genai import types
        from analyzer import ChunkNewsReport

        client = genai.Client(api_key=config.gemini_api_key)
        date_str = datetime.now().strftime("%Y-%m-%d")

        all_extracted_stories: List[NewsStory] = []
        batch_size = 40

        logger.info(f"Processing all {len(raw_stories)} Business Standard stories in batches of {batch_size}...")

        for i in range(0, len(raw_stories), batch_size):
            batch = raw_stories[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(raw_stories) + batch_size - 1) // batch_size

            logger.info(f"Analyzing Business Standard Batch {batch_num}/{total_batches} ({len(batch)} articles)...")

            prompt = f"""
You are a senior financial editor at FinBrief.
Below is a batch of {len(batch)} distinct news articles published by Business Standard ({date_str}).

TASK:
Exhaustively review and classify EVERY single article in this batch. Do not omit any story.
Assign each story strictly to ONE of these 10 categories:
1. Economy
2. Policy
3. Sector
4. IPO
5. Market
6. Trade
7. Corporate Events
8. Corporate Appointments
9. International News
10. Others

For each story provide:
- headline (exact title)
- category (exact match to 1 of 10)
- brief_details (2-3 sentences)
- bullet_points (3-5 key facts, numbers, dates)
- page_numbers (e.g. 'BS {batch[0].get("desk", "News Desk")}')
- importance ('High', 'Medium', or 'Low')

Raw Stories:
{json.dumps(batch, indent=2)}
"""

            candidate_models = ["gemini-flash-lite-latest", config.gemini_model]
            response_text = None

            for model_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ChunkNewsReport,
                            temperature=0.1,
                        )
                    )
                    response_text = response.text
                    break
                except Exception as e:
                    logger.warning(f"Batch {batch_num} call with '{model_name}' note: {e}")
                    time.sleep(2)

            if response_text:
                try:
                    batch_data = json.loads(response_text)
                    chunk_rep = ChunkNewsReport.model_validate(batch_data)
                    all_extracted_stories.extend(chunk_rep.chunk_stories)
                    logger.info(f"✅ Batch {batch_num}: extracted {len(chunk_rep.chunk_stories)} stories.")
                except Exception as e:
                    logger.error(f"Error parsing batch {batch_num}: {e}")

        summary = (
            f"Business Standard daily comprehensive edition covers {len(all_extracted_stories)} financial and corporate developments. "
            f"Key coverage spans macroeconomic data, financial sector liquidity, capital markets, IPO filings, industrial policy, and international trade."
        )

        report = NewspaperEditionReport(
            edition_date=date_str,
            total_pages_analyzed=len(all_extracted_stories),
            edition_summary=summary,
            major_stories=all_extracted_stories,
        )

        # Save local JSON and Markdown
        json_path = self.output_dir / f"news_report_bs_{date_str}.json"
        md_path = self.output_dir / f"news_report_bs_{date_str}.md"

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        from analyzer import GeminiNewsAnalyzer
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(GeminiNewsAnalyzer.render_markdown_report(report))

        logger.info(f"Saved Business Standard report ({len(report.major_stories)} stories) to: {json_path}")

        # Upload to Cloudflare R2
        upload_to_r2(json_path, f"reports/{json_path.name}")
        upload_to_r2(md_path, f"reports/{md_path.name}")

        # Save to Neon DB
        save_to_neon(report, source="business_standard")

        return report


def run_bs_pipeline() -> NewspaperEditionReport:
    fetcher = BusinessStandardFetcher()
    stories = fetcher.fetch_all_raw_articles()
    return fetcher.analyze_and_bifurcate(stories)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    rep = run_bs_pipeline()
    print(f"\n🎉 Business Standard Complete: {len(rep.major_stories)} bifurcated stories!")
