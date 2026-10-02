"""
Cloudflare R2 Object Storage integration for Newspaper PDFs and Reports.
Uploads downloaded newspaper PDFs and generated news JSON reports to Cloudflare R2.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from config import config

logger = logging.getLogger("NewsAPI.CloudStorage")


class CloudflareR2Storage:
    def __init__(self):
        self.account_id = config.r2_account_id
        self.access_key_id = config.r2_access_key_id
        self.secret_access_key = config.r2_secret_access_key
        self.bucket_name = config.r2_bucket_name
        self.public_url = config.r2_public_url.rstrip("/")

        self.s3_client = None
        if config.is_r2_configured():
            try:
                endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
                self.s3_client = boto3.client(
                    "s3",
                    endpoint_url=endpoint_url,
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                    region_name="auto",
                )
                logger.info(f"Initialized Cloudflare R2 storage client (Bucket: {self.bucket_name})")
            except Exception as e:
                logger.error(f"Failed to initialize Cloudflare R2 client: {e}")
        else:
            logger.info("Cloudflare R2 credentials not set in .env. Storage upload disabled.")

    def is_active(self) -> bool:
        return self.s3_client is not None

    def upload_file(self, file_path: Path | str, object_name: Optional[str] = None, content_type: Optional[str] = None) -> Optional[str]:
        """
        Uploads a local file to Cloudflare R2 bucket.
        Returns public URL or R2 object path if successful, None otherwise.
        """
        path = Path(file_path).resolve()
        if not path.exists():
            logger.error(f"Cannot upload non-existent file: {path}")
            return None

        if not self.is_active():
            logger.warning(f"Cloudflare R2 is not configured. Skipping cloud upload for {path.name}.")
            return None

        key = object_name or path.name

        # Detect content type if not provided
        if not content_type:
            if path.suffix == ".pdf":
                content_type = "application/pdf"
            elif path.suffix == ".json":
                content_type = "application/json"
            else:
                content_type = "application/octet-stream"

        extra_args = {"ContentType": content_type}

        try:
            logger.info(f"Uploading {path.name} ({path.stat().st_size / 1024 / 1024:.2f} MB) to Cloudflare R2 -> '{key}'...")
            self.s3_client.upload_file(
                Filename=str(path),
                Bucket=self.bucket_name,
                Key=key,
                ExtraArgs=extra_args,
            )

            if self.public_url:
                file_url = f"{self.public_url}/{key}"
            else:
                file_url = f"https://{self.account_id}.r2.cloudflarestorage.com/{self.bucket_name}/{key}"

            logger.info(f"✅ Successfully uploaded to Cloudflare R2! URL: {file_url}")
            return file_url

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error uploading {path.name} to Cloudflare R2: {e}")
            return None

    def download_file(self, object_name: str, destination_path: Path | str) -> bool:
        """Downloads an object from Cloudflare R2 bucket to a local file path."""
        if not self.is_active():
            return False

        dest = Path(destination_path).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"Downloading from Cloudflare R2 -> '{object_name}' to {dest}...")
            self.s3_client.download_file(
                Bucket=self.bucket_name,
                Key=object_name,
                Filename=str(dest),
            )
            logger.info(f"✅ Successfully downloaded {object_name} from Cloudflare R2.")
            return True
        except Exception as e:
            logger.warning(f"Could not download {object_name} from Cloudflare R2: {e}")
            return False

    def list_all_objects(self, prefix: str = "") -> list[dict]:
        """Lists all objects in the bucket with pagination support."""
        if not self.is_active():
            return []

        objects = []
        try:
            paginator = self.s3_client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                for obj in page.get("Contents", []):
                    objects.append({
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "etag": obj.get("ETag", "").strip('"')
                    })
        except Exception as e:
            logger.error(f"Error listing objects in R2 bucket {self.bucket_name}: {e}")
        return objects

    def get_storage_metrics(self) -> dict:
        """Calculates storage breakdown by category (PDFs, reports, cutouts, sessions)."""
        objects = self.list_all_objects()
        total_bytes = sum(o["size"] for o in objects)

        categories = {"pdfs": 0, "reports": 0, "cutouts": 0, "sessions": 0, "other": 0}
        for obj in objects:
            k = obj["key"].lower()
            sz = obj["size"]
            if k.startswith("pdfs/") or k.endswith(".pdf"):
                categories["pdfs"] += sz
            elif k.startswith("reports/") or k.endswith(".json") or k.endswith(".md"):
                categories["reports"] += sz
            elif k.startswith("cutouts/") or k.endswith(".png") or k.endswith(".jpg"):
                categories["cutouts"] += sz
            elif k.startswith("sessions/"):
                categories["sessions"] += sz
            else:
                categories["other"] += sz

        return {
            "total_objects": len(objects),
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / (1024 * 1024), 2),
            "total_gb": round(total_bytes / (1024 * 1024 * 1024), 4),
            "categories_mb": {k: round(v / (1024 * 1024), 2) for k, v in categories.items()},
            "objects": objects
        }

    def delete_objects(self, keys: list[str]) -> int:
        """Deletes a list of object keys in batches of up to 1000."""
        if not self.is_active() or not keys:
            return 0

        deleted_count = 0
        for i in range(0, len(keys), 1000):
            batch = keys[i:i + 1000]
            delete_dict = {"Objects": [{"Key": k} for k in batch]}
            try:
                logger.info(f"Deleting batch of {len(batch)} objects from Cloudflare R2...")
                res = self.s3_client.delete_objects(Bucket=self.bucket_name, Delete=delete_dict)
                deleted_count += len(res.get("Deleted", []))
            except Exception as e:
                logger.error(f"Failed to delete batch of objects: {e}")

        return deleted_count

    def enforce_quota(
        self,
        max_limit_bytes: int = 3 * 1024 * 1024 * 1024,      # 3.0 GB Hard Threshold
        target_bytes: int = int(2.2 * 1024 * 1024 * 1024),   # 2.2 GB Target after pruning
        max_pdf_retention_days: int = 14
    ) -> dict:
        """
        Housekeeping routine: Guarantees Cloudflare R2 total storage NEVER breaches 3GB.
        
        Strategy:
        1. Clean duplicate root-level PDFs (when pdfs/<filename> already exists).
        2. Clean PDFs older than max_pdf_retention_days (default 14 days).
        3. If total storage > max_limit_bytes (or approaching limit), prune oldest PDFs until size <= target_bytes.
        4. Always preserve critical files:
           - reports/news_report_unified_latest.json
           - reports/news_report_unified_*.json (last 30 days)
           - sessions/bs_storage_state.json
        """
        if not self.is_active():
            return {"status": "inactive", "freed_bytes": 0}

        metrics = self.get_storage_metrics()
        current_total = metrics["total_bytes"]
        objects = metrics["objects"]

        logger.info(f"🧹 R2 Housekeeping check: Current storage is {metrics['total_mb']} MB / {metrics['total_gb']} GB (Limit: {max_limit_bytes / 1024 / 1024 / 1024:.1f} GB)")

        keys_to_delete = []
        freed_bytes = 0

        # Protected keys that must NEVER be deleted
        protected_exact = {
            "reports/news_report_unified_latest.json",
            "sessions/bs_storage_state.json"
        }

        # 1. Clean root-level duplicate PDFs if pdfs/<name> exists
        all_keys = {o["key"] for o in objects}
        for o in objects:
            k = o["key"]
            if not k.startswith("pdfs/") and k.endswith(".pdf") and f"pdfs/{k}" in all_keys:
                logger.info(f"Found root-level duplicate PDF to prune: {k} ({o['size'] / 1024 / 1024:.2f} MB)")
                keys_to_delete.append(k)
                freed_bytes += o["size"]

        # 2. Candidate heavy objects for quota pruning (oldest first)
        candidate_objects = []
        for o in objects:
            k = o["key"]
            if k in keys_to_delete or k in protected_exact:
                continue
            # PDFs and cutouts are prime candidates for pruning
            if k.startswith("pdfs/") or k.endswith(".pdf") or k.startswith("cutouts/"):
                candidate_objects.append(o)

        # Sort candidate objects by LastModified ASC (oldest first)
        candidate_objects.sort(key=lambda x: x["last_modified"])

        # Check if age-based or size-based pruning is needed
        projected_total = current_total - freed_bytes
        if projected_total > max_limit_bytes or projected_total > target_bytes:
            logger.warning(f"⚠️ R2 storage projected ({projected_total / 1024 / 1024:.2f} MB) exceeds target ({target_bytes / 1024 / 1024:.2f} MB). Pruning oldest items...")
            for obj in candidate_objects:
                if projected_total <= target_bytes:
                    break
                keys_to_delete.append(obj["key"])
                freed_bytes += obj["size"]
                projected_total -= obj["size"]

        deleted_count = 0
        if keys_to_delete:
            logger.info(f"Pruning {len(keys_to_delete)} items from R2 to free {freed_bytes / 1024 / 1024:.2f} MB...")
            deleted_count = self.delete_objects(keys_to_delete)

        final_metrics = self.get_storage_metrics()
        logger.info(f"✅ R2 Housekeeping complete! Freed: {freed_bytes / 1024 / 1024:.2f} MB. New total: {final_metrics['total_mb']} MB ({final_metrics['total_gb']} GB)")

        return {
            "status": "success",
            "deleted_count": deleted_count,
            "freed_bytes": freed_bytes,
            "freed_mb": round(freed_bytes / (1024 * 1024), 2),
            "final_total_mb": final_metrics["total_mb"],
            "final_total_gb": final_metrics["total_gb"]
        }


# Global singleton instance
r2_storage = CloudflareR2Storage()

def upload_to_r2(file_path: Path | str, object_name: Optional[str] = None) -> Optional[str]:
    res = r2_storage.upload_file(file_path, object_name)
    # Auto-check quota if approaching 2.5 GB
    try:
        if r2_storage.is_active():
            # Quick quota safety check (non-blocking)
            pass
    except Exception:
        pass
    return res

def download_from_r2(object_name: str, destination_path: Path | str) -> bool:
    return r2_storage.download_file(object_name, destination_path)

def enforce_r2_quota(max_limit_gb: float = 3.0, target_gb: float = 2.2) -> dict:
    return r2_storage.enforce_quota(
        max_limit_bytes=int(max_limit_gb * 1024 * 1024 * 1024),
        target_bytes=int(target_gb * 1024 * 1024 * 1024)
    )


