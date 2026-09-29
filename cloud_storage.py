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


# Global singleton instance
r2_storage = CloudflareR2Storage()

def upload_to_r2(file_path: Path | str, object_name: Optional[str] = None) -> Optional[str]:
    return r2_storage.upload_file(file_path, object_name)

def download_from_r2(object_name: str, destination_path: Path | str) -> bool:
    return r2_storage.download_file(object_name, destination_path)

