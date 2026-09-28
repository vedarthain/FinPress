"""
Business Standard Complete 36-Page ePaper PDF & Edition Downloader.
Downloads full edition zipped PDFs or compiles all 1-36 page high-resolution editions
from https://epaper.business-standard.com into a single unified master PDF.
Uploads the PDF to Cloudflare R2 and triggers Gemini Flash institutional analysis.
"""

import io
import os
import re
import zipfile
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import requests
from playwright.sync_api import sync_playwright

from config import config
from cloud_storage import upload_to_r2
from analyzer import NewspaperEditionReport, analyze_newspaper_pdf

logger = logging.getLogger("NewsAPI.BSEpaperDownloader")


class BusinessStandardSessionError(Exception):
    """Raised when Business Standard subscriber authentication or ePaper download fails."""
    pass


class BusinessStandardEpaperDownloader:
    def __init__(self, download_dir: Optional[Path] = None):
        self.download_dir = download_dir or config.download_dir
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = config.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.date_str = datetime.now().strftime("%Y-%m-%d")

    def download_from_zip(self, zip_path_or_url: str) -> Path:
        """Extracts and merges all page PDFs from a Business Standard single zipped PDF edition."""
        target_pdf = self.download_dir / f"business_standard_{self.date_str}.pdf"
        logger.info(f"Processing Business Standard zipped edition: {zip_path_or_url}")

        if zip_path_or_url.startswith("http://") or zip_path_or_url.startswith("https://"):
            resp = requests.get(zip_path_or_url, timeout=60)
            resp.raise_for_status()
            zip_bytes = io.BytesIO(resp.content)
            z = zipfile.ZipFile(zip_bytes)
        else:
            z = zipfile.ZipFile(zip_path_or_url)

        pdf_names = sorted([name for name in z.namelist() if name.lower().endswith(".pdf")])
        if not pdf_names:
            raise BusinessStandardSessionError("Zip archive contained no valid page PDF files.")

        logger.info(f"Found {len(pdf_names)} page PDFs inside Business Standard zip archive.")

        if len(pdf_names) == 1:
            # Single consolidated PDF inside zip
            with open(target_pdf, "wb") as f:
                f.write(z.read(pdf_names[0]))
        else:
            # Multiple page PDFs inside zip - merge with PdfWriter
            try:
                from pypdf import PdfWriter
            except ImportError:
                from PyPDF2 import PdfWriter

            writer = PdfWriter()
            for name in pdf_names:
                writer.append(io.BytesIO(z.read(name)))

            with open(target_pdf, "wb") as f:
                writer.write(f)
            writer.close()

        logger.info(f"Successfully compiled all pages into: {target_pdf} ({target_pdf.stat().st_size / (1024*1024):.2f} MB)")
        
        # Upload PDF to Cloudflare R2
        upload_to_r2(target_pdf, f"pdfs/{target_pdf.name}")
        upload_to_r2(target_pdf, target_pdf.name)

        return target_pdf

    def download_full_epaper(
        self,
        epaper_url: str = "https://epaper.business-standard.com/bs_new/index.php?rt=main/mainpage#1",
        storage_state_file: str = "bs_storage_state.json"
    ) -> Path:
        """
        Launches Playwright subscriber session to download all 1-36 pages or full zipped edition.
        Raises BusinessStandardSessionError if authentication or session fails.
        """
        state_path = Path(storage_state_file)
        if not state_path.exists():
            # Attempt to restore from BS_STORAGE_STATE_BASE64 environment variable
            b64_env = os.environ.get("BS_STORAGE_STATE_BASE64", "").strip()
            if b64_env:
                try:
                    import re, base64, json
                    clean_b64 = re.sub(r'[^A-Za-z0-9+/=]', '', b64_env)
                    pad_len = len(clean_b64) % 4
                    if pad_len != 0:
                        clean_b64 += '=' * (4 - pad_len)
                    decoded_bytes = base64.b64decode(clean_b64)
                    json.loads(decoded_bytes.decode('utf-8', errors='ignore'))
                    state_path.write_bytes(decoded_bytes)
                    logger.info(f"Restored '{storage_state_file}' from BS_STORAGE_STATE_BASE64 environment variable.")
                except Exception as e:
                    logger.warning(f"Failed to auto-decode BS_STORAGE_STATE_BASE64: {e}")

        if not state_path.exists():
            error_msg = (
                f"❌ CRITICAL SESSION FAILURE: Business Standard session state '{storage_state_file}' was not found. "
                "Unable to authenticate with https://epaper.business-standard.com. "
                "Please configure 'BS_STORAGE_STATE_BASE64' in GitHub Secrets or generate 'bs_storage_state.json' locally."
            )
            logger.error(error_msg)
            raise BusinessStandardSessionError(error_msg)

        target_pdf = self.download_dir / f"business_standard_{self.date_str}.pdf"
        logger.info(f"Launching subscriber session for Business Standard 36-page ePaper: {epaper_url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=config.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-web-security"
                ]
            )
            context = browser.new_context(
                storage_state=str(state_path),
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                accept_downloads=True
            )
            page = context.new_page()

            try:
                # Prime session on root domain first to ensure SSO cookies propagate to epaper sub-domain
                try:
                    logger.info("Priming subscriber session on business-standard.com...")
                    page.goto("https://www.business-standard.com", timeout=30000, wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)
                except Exception as e:
                    logger.warning(f"Root domain warmup notice: {e}")

                logger.info(f"Navigating to ePaper reader: {epaper_url}")
                page.goto(epaper_url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)

                current_url = page.url
                page_title = page.title()

                # Explicitly detect authentication failure or redirect to login/sso
                if "sso-login" in current_url or "login" in current_url.lower() or "access denied" in page_title.lower():
                    error_msg = (
                        f"❌ SUBSCRIBER SESSION EXPIRED: Business Standard redirected to login / access denied. "
                        f"(URL: {current_url}, Title: '{page_title}'). "
                        "The subscriber session token has expired or is invalid. Please refresh the login session state."
                    )
                    logger.error(error_msg)
                    raise BusinessStandardSessionError(error_msg)

                # 1. Trigger Read Offline Modal
                logger.info("Opening Business Standard Read Offline edition download modal...")
                try:
                    readoff_btn = page.wait_for_selector('.readoffline, button[title="Read offline"], img[src*="read-off"]', timeout=15000)
                    if readoff_btn:
                        readoff_btn.click()
                except Exception:
                    page.evaluate('() => { const b = document.querySelector(".readoffline, button[title=\'Read offline\'], img[src*=\'read-off\']"); if (b) b.click(); }')
                page.wait_for_timeout(3000)

                # 2. Select Full Edition Download
                logger.info("Triggering full edition download action...")
                try:
                    full_down = page.wait_for_selector('a.editionall, .fulleditiondown a, .fulleditiondown, .sectiondownlink', timeout=10000)
                    if full_down:
                        full_down.click()
                except Exception:
                    page.evaluate('() => { const b = document.querySelector("a.editionall, .fulleditiondown a, .fulleditiondown, .sectiondownlink"); if (b) b.click(); }')
                page.wait_for_timeout(2000)

                # 3. Confirm Download in Modal & Intercept Download
                confirm_btn = None
                try:
                    confirm_btn = page.wait_for_selector('.readoffeditdownload, #readofffulleditiondownload button.btn-primary', timeout=10000)
                except Exception:
                    pass

                download_path = None
                try:
                    with page.expect_download(timeout=45000) as download_info:
                        if confirm_btn:
                            confirm_btn.click()
                        else:
                            page.evaluate('() => { const b = document.querySelector(".readoffeditdownload, #readofffulleditiondownload button.btn-primary, a.readoffeditdownload"); if (b) b.click(); }')
                        logger.info("Clicked confirmation button. Receiving full edition download stream...")

                    download = download_info.value
                    download_path = self.download_dir / download.suggested_filename
                    download.save_as(str(download_path))
                    logger.info(f"Downloaded full edition archive: {download_path} ({download_path.stat().st_size / (1024*1024):.2f} MB)")
                except Exception as zip_err:
                    logger.warning(f"Full edition zip download attempt: {zip_err}. Attempting Page-by-Page download fallback...")

                if download_path:
                    browser.close()
                    if str(download_path).lower().endswith(".zip"):
                        return self.download_from_zip(str(download_path))
                    elif str(download_path).lower().endswith(".pdf"):
                        download_path.rename(target_pdf)
                        upload_to_r2(target_pdf, f"pdfs/{target_pdf.name}")
                        upload_to_r2(target_pdf, target_pdf.name)
                        return target_pdf

                # 4. Fallback: Page-by-Page Single Page Download & Compilation
                logger.info("Executing Page-by-Page single PDF download strategy (Pages 1 to 36)...")
                page_links = page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('a.off-downld, [href*=\"singlepage\"], .tmb-lst a')).map(a => a.href).filter(h => h && h.includes('singlepage'));
                }''')

                if not page_links:
                    # Collect all single pages from readoffline container
                    page_links = page.evaluate('''() => {
                        const links = [];
                        document.querySelectorAll('[data-pageno]').forEach(el => {
                            const pagename = el.getAttribute('data-pagename');
                            const pageno = el.getAttribute('data-pageno');
                            if (pagename) links.push({ pagename, pageno });
                        });
                        return links;
                    }''')

                single_page_pdfs = []
                logger.info(f"Identified {len(page_links)} single-page download references.")

                # Try saving pages
                if page_links:
                    try:
                        from pypdf import PdfWriter
                    except ImportError:
                        from PyPDF2 import PdfWriter

                    writer = PdfWriter()
                    for idx, link_info in enumerate(page_links, start=1):
                        try:
                            logger.info(f"Fetching Business Standard Page {idx}...")
                            with page.expect_download(timeout=20000) as p_down_info:
                                page.evaluate(f'''(idx) => {{
                                    const els = document.querySelectorAll('a.off-downld, .tmb-lst a, [data-pageno]');
                                    if (els[idx-1]) els[idx-1].click();
                                }}''', idx)
                            p_down = p_down_info.value
                            p_path = self.download_dir / f"bs_page_{idx}_{self.date_str}.pdf"
                            p_down.save_as(str(p_path))
                            writer.append(str(p_path))
                            single_page_pdfs.append(p_path)
                        except Exception as p_err:
                            logger.warning(f"Could not download single page {idx}: {p_err}")

                    if single_page_pdfs:
                        with open(target_pdf, "wb") as f:
                            writer.write(f)
                        writer.close()
                        logger.info(f"Successfully compiled {len(single_page_pdfs)} single pages into: {target_pdf} ({target_pdf.stat().st_size / (1024*1024):.2f} MB)")
                        upload_to_r2(target_pdf, f"pdfs/{target_pdf.name}")
                        upload_to_r2(target_pdf, target_pdf.name)
                        browser.close()
                        return target_pdf

                raise BusinessStandardSessionError("❌ Could not download Business Standard ePaper via full zip or page-by-page. Session may require re-authentication.")

            except BusinessStandardSessionError:
                raise
            except Exception as e:
                error_msg = f"❌ Business Standard ePaper download error: {e}"
                logger.error(error_msg)
                raise BusinessStandardSessionError(error_msg) from e
            finally:
                try:
                    browser.close()
                except Exception:
                    pass


def run_bs_full_edition_pipeline(custom_pdf_or_zip: Optional[str] = None) -> NewspaperEditionReport:
    """
    Executes the comprehensive Business Standard 36-page analysis.
    Explicitly raises BusinessStandardSessionError on authentication / download failure.
    """
    downloader = BusinessStandardEpaperDownloader()
    pdf_path = None

    if custom_pdf_or_zip:
        if custom_pdf_or_zip.lower().endswith(".zip"):
            pdf_path = downloader.download_from_zip(custom_pdf_or_zip)
        else:
            pdf_path = Path(custom_pdf_or_zip)
    else:
        pdf_path = downloader.download_full_epaper()

    if pdf_path and pdf_path.exists():
        logger.info(f"Analyzing full {pdf_path.name} ({pdf_path.stat().st_size / (1024*1024):.2f} MB) via Gemini 3.8 Flash...")
        report = analyze_newspaper_pdf(pdf_path)
        return report

    raise BusinessStandardSessionError("Business Standard master PDF was not generated.")

