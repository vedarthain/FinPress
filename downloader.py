"""
Playwright & Public API Downloader Module for Newspaper PDF Editions.
Fetches high-resolution page images from Financial Express public API endpoints
and compiles them into a complete PDF edition without requiring login credentials.
"""

import re
import asyncio
import logging
from pathlib import Path
from typing import List, Optional

import img2pdf
import requests
from playwright.async_api import async_playwright

from config import config
from cloud_storage import upload_to_r2

logger = logging.getLogger(__name__)


class NewspaperDownloader:
    def __init__(self, download_dir: Optional[Path] = None):
        self.download_dir = download_dir or config.download_dir
        self.download_dir.mkdir(parents=True, exist_ok=True)

    async def get_latest_issue_id(self, target_url: str) -> str:
        """Navigates to the edition page and resolves the latest issue ID."""
        logger.info(f"Resolving edition URL: {target_url}...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=config.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            final_url = page.url
            await browser.close()

            logger.info(f"Resolved issue URL: {final_url}")
            match = re.search(r"/(\d{6,8})/", final_url)
            if match:
                return match.group(1)
            raise RuntimeError(f"Could not extract issue ID from URL: {final_url}")

    def fetch_page_images(self, issue_id: str) -> List[bytes]:
        """Downloads all high-resolution page images using public API endpoint."""
        meta_url = f"https://epaper.financialexpress.com/pagemeta/get/{issue_id}/1-100"
        logger.info(f"Fetching page metadata from: {meta_url}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "https://epaper.financialexpress.com/"
        }

        resp = requests.get(meta_url, headers=headers)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch metadata (Status: {resp.status_code})")

        meta_data = resp.json()
        page_numbers = sorted(meta_data.keys(), key=lambda x: int(x))
        logger.info(f"Discovered {len(page_numbers)} pages for Issue ID #{issue_id}.")

        image_bytes_list = []
        for pnum in page_numbers:
            page_info = meta_data[pnum]
            levels = page_info.get("levels", {})

            # Select high-resolution chunk URL
            img_url = None
            for level in ["leveldefault", "level1", "level0"]:
                if level in levels and "chunks" in levels[level] and len(levels[level]["chunks"]) > 0:
                    img_url = levels[level]["chunks"][0]["url"]
                    break

            if not img_url:
                continue

            logger.info(f"Downloading Page {pnum}/{len(page_numbers)}...")
            img_resp = requests.get(img_url, headers=headers)
            if img_resp.status_code == 200:
                image_bytes_list.append(img_resp.content)

        return image_bytes_list

    async def download_today_pdf(self, target_url: Optional[str] = None) -> Path:
        """
        Main method to download today's PDF edition.
        No login or credentials required.
        """
        url = target_url or config.newspaper_url
        issue_id = await self.get_latest_issue_id(url)

        logger.info(f"Fetching pages for Issue ID #{issue_id}...")
        image_bytes = self.fetch_page_images(issue_id)

        if not image_bytes:
            raise RuntimeError(f"Failed to retrieve page images for issue {issue_id}")

        output_pdf_path = self.download_dir / f"edition_{issue_id}.pdf"
        logger.info(f"Compiling {len(image_bytes)} page images into PDF document...")

        pdf_data = img2pdf.convert(image_bytes)
        with open(output_pdf_path, "wb") as f:
            f.write(pdf_data)

        # Upload to Cloudflare R2 Object Storage if configured
        cloud_url = upload_to_r2(output_pdf_path, f"pdfs/Financial_Express_Mumbai_{issue_id}.pdf")
        if cloud_url:
            logger.info(f"Cloudflare R2 PDF URL: {cloud_url}")

        logger.info(f"Successfully created PDF: {output_pdf_path} ({output_pdf_path.stat().st_size / (1024*1024):.2f} MB)")
        return output_pdf_path


def run_downloader(url: Optional[str] = None) -> Path:
    """Synchronous helper function to run download task."""
    downloader = NewspaperDownloader()
    return asyncio.run(downloader.download_today_pdf(url))
