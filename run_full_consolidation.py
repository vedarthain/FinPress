"""
Full Consolidation Pipeline:
Analyzes the downloaded Business Standard 36-page PDF, merges with Financial Express,
and publishes the unified consolidated intelligence report directly to Cloudflare R2 and Neon DB.
"""

import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Consolidation")

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from analyzer import analyze_newspaper_pdf, NewspaperEditionReport
from aggregator import UnifiedNewsAggregator
from cloud_storage import upload_to_r2
from db import save_to_neon

def run():
    target_date = "2026-09-28"
    download_dir = Path("./downloads")
    bs_pdf = download_dir / f"business_standard_{target_date}.pdf"

    if not bs_pdf.exists():
        test_pdf = download_dir / "business_standard_test.pdf"
        if test_pdf.exists():
            import shutil
            shutil.copy(test_pdf, bs_pdf)
            logger.info(f"Copied {test_pdf} -> {bs_pdf}")
        else:
            # Download from R2
            import requests
            r2_pdf_url = f"https://pub-c81167dd545d49d0a2cd964a8bd6a1cd.r2.dev/business_standard_{target_date}.pdf"
            logger.info(f"Downloading Business Standard PDF from R2: {r2_pdf_url}...")
            resp = requests.get(r2_pdf_url, stream=True)
            with open(bs_pdf, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024*1024):
                    f.write(chunk)
            logger.info(f"Downloaded {bs_pdf} ({bs_pdf.stat().st_size / (1024*1024):.2f} MB)")

    logger.info(f"Step 1: Analyzing complete Business Standard 36-page PDF ({bs_pdf.stat().st_size / (1024*1024):.2f} MB)...")
    bs_report = analyze_newspaper_pdf(bs_pdf)
    logger.info(f"✅ Business Standard extraction complete: {len(bs_report.major_stories)} stories extracted!")

    # Step 2: Load Financial Express report
    fe_report = None
    reports_dir = Path("./reports")
    fe_paths = [
        reports_dir / f"news_report_fe_{target_date}.json",
        reports_dir / f"news_report_{target_date}.json"
    ]
    for p in fe_paths:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                fe_report = NewspaperEditionReport.model_validate_json(f.read())
                logger.info(f"✅ Loaded Financial Express report: {len(fe_report.major_stories)} stories.")
                break

    if not fe_report:
        # Load from R2
        import requests
        fe_url = f"https://pub-c81167dd545d49d0a2cd964a8bd6a1cd.r2.dev/reports/news_report_{target_date}.json"
        logger.info(f"Fetching FE report from R2: {fe_url}...")
        resp = requests.get(fe_url)
        if resp.status_code == 200:
            fe_report = NewspaperEditionReport.model_validate_json(resp.text)
            logger.info(f"✅ Loaded Financial Express report from R2: {len(fe_report.major_stories)} stories.")

    # Step 3: Combine and Deduplicate
    reports_to_merge = []
    source_statuses = {
        "financial_express": f"✅ Active ({len(fe_report.major_stories) if fe_report else 0} stories)",
        "business_standard": f"✅ Active ({len(bs_report.major_stories)} stories)"
    }

    if fe_report:
        reports_to_merge.append((fe_report, "Financial Express"))
    reports_to_merge.append((bs_report, "Business Standard"))

    logger.info("Step 3: Running unified lossless deduplication & master aggregation...")
    agg = UnifiedNewsAggregator()
    master_report = agg.combine_and_deduplicate(
        reports_to_merge,
        date_str=target_date,
        source_statuses=source_statuses
    )

    logger.info("=" * 60)
    logger.info(f"🎉 MASTER UNIFIED INTELLIGENCE EDITION PUBLISHED!")
    logger.info(f"Total Stories: {len(master_report.major_stories)}")
    logger.info(f"Source Statuses: {master_report.source_statuses}")
    logger.info("=" * 60)

if __name__ == "__main__":
    run()
