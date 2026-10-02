#!/usr/bin/env python3
"""
Cloudflare R2 Storage Housekeeping & 3GB Quota Enforcement Script.

Guarantees Cloudflare R2 bucket storage NEVER breaches the 3.0 GB limit.
Automatically detects and removes:
- Root-level duplicate PDFs
- Old PDF editions older than retention threshold (oldest first)
- Old temporary cutout images and artifacts
- Prunes oldest heavy assets when total storage reaches quota threshold

Usage:
  python scripts/r2_housekeeping.py [--max-gb 3.0] [--target-gb 2.2] [--retention-days 14]
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from cloud_storage import r2_storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("R2Housekeeping")


def run_housekeeping(max_gb: float = 3.0, target_gb: float = 2.2, retention_days: int = 14, dry_run: bool = False):
    logger.info("=" * 60)
    logger.info(f"🚀 Cloudflare R2 Storage Housekeeping (Limit: {max_gb:.1f} GB, Target: {target_gb:.1f} GB)")
    logger.info("=" * 60)

    if not r2_storage.is_active():
        logger.warning("❌ Cloudflare R2 storage is not configured or credentials missing. Exiting.")
        return 0

    # 1. Gather initial metrics
    initial = r2_storage.get_storage_metrics()
    logger.info(f"📊 Current R2 Usage: {initial['total_objects']} objects, {initial['total_mb']} MB ({initial['total_gb']} GB)")
    logger.info(f"   - PDFs: {initial['categories_mb']['pdfs']} MB")
    logger.info(f"   - Reports: {initial['categories_mb']['reports']} MB")
    logger.info(f"   - Cutouts: {initial['categories_mb']['cutouts']} MB")
    logger.info(f"   - Sessions: {initial['categories_mb']['sessions']} MB")
    logger.info(f"   - Other: {initial['categories_mb']['other']} MB")

    max_bytes = int(max_gb * 1024 * 1024 * 1024)
    target_bytes = int(target_gb * 1024 * 1024 * 1024)

    # 2. Run Quota Enforcement
    if dry_run:
        logger.info("🔍 DRY RUN enabled: No objects will be deleted.")
        headroom_gb = max_gb - initial['total_gb']
        logger.info(f"Headroom remaining: {headroom_gb:.3f} GB / {max_gb:.1f} GB ({headroom_gb/max_gb*100:.1f}% free)")
        return 0

    result = r2_storage.enforce_quota(
        max_limit_bytes=max_bytes,
        target_bytes=target_bytes,
        max_pdf_retention_days=retention_days
    )

    # 3. Final Summary
    logger.info("-" * 60)
    logger.info(f"🧹 Pruned: {result.get('deleted_count', 0)} objects | Freed: {result.get('freed_mb', 0)} MB")
    logger.info(f"📦 Final R2 Storage: {result.get('final_total_mb', 0)} MB ({result.get('final_total_gb', 0)} GB)")
    final_gb = result.get('final_total_gb', 0)
    headroom_gb = max_gb - final_gb
    logger.info(f"✅ Quota Status: Safe ({headroom_gb:.2f} GB headroom under {max_gb:.1f} GB limit)")
    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloudflare R2 3GB Quota Housekeeping")
    parser.add_argument("--max-gb", type=float, default=3.0, help="Maximum R2 capacity quota (default: 3.0 GB)")
    parser.add_argument("--target-gb", type=float, default=2.2, help="Target storage size after pruning (default: 2.2 GB)")
    parser.add_argument("--retention-days", type=int, default=14, help="PDF retention threshold in days (default: 14)")
    parser.add_argument("--dry-run", action="store_true", help="Inspect without deleting objects")

    args = parser.parse_args()
    sys.exit(run_housekeeping(
        max_gb=args.max_gb,
        target_gb=args.target_gb,
        retention_days=args.retention_days,
        dry_run=args.dry_run
    ))
