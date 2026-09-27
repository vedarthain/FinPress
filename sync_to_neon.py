"""
One-click Neon PostgreSQL Migration & Sync Tool.
Initializes the Neon DB schema and populates all historical & latest unified newspaper reports.
"""

import json
import logging
import os
import sys
from pathlib import Path

from config import config
from db import NeonDatabase
from analyzer import NewspaperEditionReport

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NewsAPI.NeonSync")


def sync_all_reports_to_neon(database_url: str = None):
    db_url = database_url or os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("❌ DATABASE_URL is not set. Please provide it in .env or pass as an argument.")
        print("\nUsage:")
        print("  python sync_to_neon.py postgresql://user:password@ep-xyz.neon.tech/neondb?sslmode=require\n")
        return False

    neon_db = NeonDatabase(database_url=db_url)

    logger.info("🔧 Step 1: Initializing Neon PostgreSQL Schema...")
    neon_db.init_db()

    reports_dir = Path(config.output_dir)
    unified_files = sorted(reports_dir.glob("news_report_unified_*.json"))

    if not unified_files:
        logger.warning("No unified report files found in reports/ directory.")
        return True

    logger.info(f"📦 Step 2: Found {len(unified_files)} report files. Syncing to Neon...")

    synced_count = 0
    for f in unified_files:
        if "latest" in f.name:
            continue
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                report = NewspaperEditionReport.model_validate(data)
                success = neon_db.save_report(report, source="unified")
                if success:
                    synced_count += 1
                    logger.info(f"✅ Synced edition {report.edition_date} ({len(report.major_stories)} stories) into Neon DB.")
        except Exception as e:
            logger.error(f"Error syncing {f.name}: {e}")

    # Also ensure the latest report is synced if no date-stamped file was processed
    if synced_count == 0 and (reports_dir / "news_report_unified_latest.json").exists():
        with open(reports_dir / "news_report_unified_latest.json", "r", encoding="utf-8") as fp:
            data = json.load(fp)
            report = NewspaperEditionReport.model_validate(data)
            neon_db.save_report(report, source="unified")
            logger.info(f"✅ Synced latest edition ({len(report.major_stories)} stories) into Neon DB.")
            synced_count += 1

    logger.info(f"\n🎉 Successfully synced {synced_count} edition(s) to Neon PostgreSQL!")
    return True


if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    sync_all_reports_to_neon(url_arg)
