"""
Main Pipeline Orchestrator & Daily Scheduler for Newspaper PDF Gemini Analysis.
"""

import argparse
import asyncio
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule

from config import config
from downloader import run_downloader
from bs_downloader import run_bs_pipeline
from analyzer import analyze_newspaper_pdf

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("newspaper_automation.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")


def run_pipeline(custom_url: str = None, pdf_file: str = None, source: str = "all"):
    """
    Executes the complete end-to-end automation workflow:
    - If source='all': Fetches FE & BS, deduplicates, and publishes unified report.
    - If source='financial_express': Fetches Financial Express only.
    - If source='business_standard': Fetches Business Standard only.
    """
    logger.info("==================================================")
    logger.info(f"Starting Newspaper Automation Pipeline ({source}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("==================================================")

    config.ensure_directories()
    config.validate_api_key()

    pdf_path: Path = None

    try:
        if pdf_file:
            pdf_path = Path(pdf_file).resolve()
            logger.info(f"Using pre-existing local PDF file: {pdf_path}")
            logger.info("Sending PDF to Google Gemini Flash API for analysis...")
            report = analyze_newspaper_pdf(pdf_path)
        elif source in ["all", "unified"]:
            source_statuses = {}

            logger.info("Step 1: Downloading & analyzing Financial Express edition (24 pages)...")
            fe_report = None
            try:
                pdf_path = run_downloader(url=custom_url)
                fe_report = analyze_newspaper_pdf(pdf_path)
                source_statuses["financial_express"] = f"✅ Success ({len(fe_report.major_stories)} stories extracted)"
            except Exception as e:
                err_fe = f"❌ FAILED: {e}"
                logger.error(f"[SOURCE FAILURE] Financial Express: {err_fe}")
                source_statuses["financial_express"] = err_fe

            logger.info("Step 2: Fetching & analyzing Business Standard edition (36-page ePaper & Desks)...")
            bs_report = None
            try:
                from bs_epaper_downloader import run_bs_full_edition_pipeline
                bs_report = run_bs_full_edition_pipeline()
                source_statuses["business_standard"] = f"✅ Success ({len(bs_report.major_stories)} stories extracted)"
            except Exception as e:
                err_bs = f"❌ FAILED: {e}"
                logger.error(f"[SOURCE FAILURE] Business Standard: {err_bs}")
                source_statuses["business_standard"] = err_bs

            logger.info("Step 3: Running unified multi-source deduplication & aggregation...")
            from aggregator import UnifiedNewsAggregator
            reports_to_merge = []
            if fe_report:
                reports_to_merge.append((fe_report, "Financial Express"))
            if bs_report:
                reports_to_merge.append((bs_report, "Business Standard"))

            if not reports_to_merge:
                from aggregator import run_unified_aggregation
                report = run_unified_aggregation()
            else:
                agg = UnifiedNewsAggregator()
                report = agg.combine_and_deduplicate(reports_to_merge, source_statuses=source_statuses)

        elif source in ["aggregate", "combine"]:
            logger.info("Running unified multi-source deduplication & aggregation from existing downloaded reports...")
            from aggregator import run_unified_aggregation
            report = run_unified_aggregation()
        elif source == "business_standard" or (custom_url and "business-standard" in custom_url):
            logger.info("Step 1: Fetching Business Standard daily 36-page edition...")
            from bs_epaper_downloader import run_bs_full_edition_pipeline
            try:
                report = run_bs_full_edition_pipeline(custom_pdf_or_zip=pdf_file)
            except Exception as e:
                logger.error("=" * 60)
                logger.error("❌ CRITICAL: BUSINESS STANDARD SUBSCRIBER SESSION FAILED!")
                logger.error(f"Reason: {e}")
                logger.error("=" * 60)
                raise
        else:
            logger.info("Step 1: Downloading Financial Express ePaper edition...")
            pdf_path = run_downloader(url=custom_url)
            logger.info("Step 2: Sending PDF to Google Gemini Flash API for analysis...")
            report = analyze_newspaper_pdf(pdf_path)

        logger.info("==================================================")
        logger.info("Pipeline Execution Finished! Executive Summary:")
        logger.info(f"Total Stories Extracted: {len(report.major_stories)}")
        if hasattr(report, "source_statuses") and report.source_statuses:
            logger.info(f"Source Health: {report.source_statuses}")
        logger.info(f"Summary: {report.edition_summary[:200]}...")
        logger.info("==================================================")

        # Print top stories to console
        print("\n" + "=" * 60)
        print(f"📰 DAILY NEWSPAPER REPORT - {report.edition_date}")
        if hasattr(report, "source_statuses") and report.source_statuses:
            print("-" * 60)
            print("📊 NEWSPAPER SOURCE PIPELINE HEALTH:")
            for src, stat in report.source_statuses.items():
                print(f"  • {src.replace('_', ' ').title():<20}: {stat}")
            print("-" * 60)
        print("=" * 60)
        print(f"\nSummary:\n{report.edition_summary}\n")
        print("Top Headline Stories:")
        for story in report.major_stories[:5]:
            print(f"- [{story.category}] {story.headline} ({story.page_numbers})")
            print(f"  Summary: {story.brief_details}")
            print("  Key points:")
            for bp in story.bullet_points[:3]:
                print(f"    * {bp}")
            print()
        print(f"Full reports saved to directory: {config.output_dir}")

    except Exception as e:
        logger.error(f"Error during pipeline execution: {e}", exc_info=True)
        raise e


def start_daily_scheduler(run_time: str, custom_url: str = None):
    """Schedules the pipeline to run daily at specified HH:MM time."""
    logger.info(f"Scheduling daily automation job to run every day at {run_time}...")
    
    schedule.every().day.at(run_time).do(run_pipeline, custom_url=custom_url)
    
    logger.info(f"Scheduler active. Waiting for scheduled run time '{run_time}'. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(30)


def main():
    parser = argparse.ArgumentParser(
        description="Daily Newspaper Playwright Downloader & Gemini Flash News Extractor"
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run the automation pipeline immediately once.",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run continuously in background mode with daily scheduler.",
    )
    parser.add_argument(
        "--schedule-time",
        type=str,
        default=config.schedule_time,
        help="Daily time to run in HH:MM format (default: 06:00).",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Optional target newspaper URL to download PDF from.",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="all",
        choices=["all", "unified", "financial_express", "business_standard", "aggregate", "combine"],
        help="Newspaper source ('all', 'financial_express', 'business_standard', or 'aggregate').",
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default=None,
        help="Path to an existing local PDF file to analyze directly.",
    )

    args = parser.parse_args()

    if args.daemon:
        if args.run_now:
            logger.info("Executing immediate run before starting daemon scheduler...")
            run_pipeline(custom_url=args.url, pdf_file=args.pdf, source=args.source)
        start_daily_scheduler(run_time=args.schedule_time, custom_url=args.url)
    else:
        # Default behavior is --run-now if no flags given
        run_pipeline(custom_url=args.url, pdf_file=args.pdf, source=args.source)


if __name__ == "__main__":
    main()
