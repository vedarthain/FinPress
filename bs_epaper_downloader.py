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
    """Raised when Business Standard subscriber authentication fails."""
    pass


class BusinessStandardEditionNotAvailable(Exception):
    """
    Raised when Business Standard English-Mumbai edition is not available,
    while subscriber authentication / session token was successfully verified.
    Ensures Hindi editions are strictly skipped.
    """
    pass


class BusinessStandardEpaperDownloader:
    def __init__(self, download_dir: Optional[Path] = None):
        self.download_dir = download_dir or config.download_dir
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = config.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.date_str = datetime.now().strftime("%Y-%m-%d")

    def _ensure_english_mumbai_edition(self, page) -> bool:
        """
        Verifies and selects the Business Standard English-Mumbai edition.
        Strictly refuses to download Hindi editions.
        Raises BusinessStandardEditionNotAvailable if English-Mumbai is not available while token is authenticated.
        """
        logger.info("Verifying Business Standard edition (Strict requirement: English - Mumbai, strictly no Hindi)...")
        
        # 1. Inspect current page edition text and URL
        edition_status = page.evaluate('''() => {
            const url = window.location.href;
            const title = document.title || '';
            const edEl = document.querySelector('.editionname, .current-edition, #current_edition, .edition-title, .ed-title, .edition-select, .ed-list .active, a.edition-active, .selected-edition');
            const edText = edEl ? (edEl.innerText || edEl.textContent || '').trim() : '';
            const bodyText = document.body.innerText || '';
            
            const isHindi = /hindi|हिंदी|bs_hindi/i.test(url) || /hindi|हिंदी/i.test(title) || /hindi|हिंदी/i.test(edText);
            const isMumbai = /mumbai/i.test(url) || /mumbai/i.test(title) || /mumbai/i.test(edText);
            const isEnglish = !isHindi && (/english/i.test(url) || /english/i.test(title) || /english/i.test(edText) || isMumbai);
            
            return { url, title, edText, isHindi, isMumbai, isEnglish };
        }''')
        logger.info(f"Current ePaper page status: URL='{edition_status.get('url')}', Edition='{edition_status.get('edText')}', isHindi={edition_status.get('isHindi')}, isMumbai={edition_status.get('isMumbai')}")
        
        if edition_status.get('isMumbai') and not edition_status.get('isHindi'):
            logger.info("✅ Confirmed: Business Standard English - Mumbai edition is actively loaded.")
            return True
            
        # 2. Attempt to open edition selector and select Mumbai
        logger.info("Searching for Business Standard edition selector to choose English - Mumbai...")
        selected = page.evaluate('''() => {
            const dropdowns = document.querySelectorAll('.edition-select, .editionSelect, .change-edition, #edition_dropdown, .ed-toggle, a[title*="Edition" i], .editionname, .dropdown-toggle');
            dropdowns.forEach(d => { try { d.click(); } catch(e) {} });
            
            const options = Array.from(document.querySelectorAll('a, option, .edition-item, .dropdown-menu li a, .ed-list li a, .ed-list a'));
            const mumbaiOpt = options.find(el => {
                const txt = (el.innerText || el.textContent || el.value || '').trim();
                return /mumbai/i.test(txt) && !/hindi|हिंदी/i.test(txt);
            });
            
            if (mumbaiOpt) {
                if (mumbaiOpt.tagName.toLowerCase() === 'option') {
                    const select = mumbaiOpt.closest('select');
                    if (select) {
                        select.value = mumbaiOpt.value;
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    }
                } else {
                    mumbaiOpt.click();
                    return true;
                }
            }
            return false;
        }''')
        
        if selected:
            page.wait_for_timeout(4000)
            recheck = page.evaluate('''() => {
                const url = window.location.href;
                const title = document.title || '';
                const edEl = document.querySelector('.editionname, .current-edition, #current_edition, .edition-title, .ed-list .active');
                const edText = edEl ? (edEl.innerText || '').trim() : '';
                const isHindi = /hindi|हिंदी/i.test(url) || /hindi|हिंदी/i.test(title) || /hindi|हिंदी/i.test(edText);
                const isMumbai = /mumbai/i.test(url) || /mumbai/i.test(title) || /mumbai/i.test(edText);
                return { isHindi, isMumbai };
            }''')
            if recheck.get('isMumbai') and not recheck.get('isHindi'):
                logger.info("✅ Successfully switched to Business Standard English - Mumbai edition.")
                return True
                
        # 3. Direct navigation to Mumbai edition URL if standard URL pattern exists
        try:
            logger.info("Attempting direct navigation to English - Mumbai ePaper edition URL...")
            page.goto("https://epaper.business-standard.com/bs_new/index.php?rt=main/mainpage&edition=mumbai#1", timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)
            direct_check = page.evaluate('''() => {
                const url = window.location.href;
                const title = document.title || '';
                const isHindi = /hindi|हिंदी/i.test(url) || /hindi|हिंदी/i.test(title);
                const isMumbai = /mumbai/i.test(url) || /mumbai/i.test(title);
                return { isHindi, isMumbai, url, title };
            }''')
            if direct_check.get('isMumbai') and not direct_check.get('isHindi'):
                logger.info("✅ Successfully navigated to English - Mumbai edition URL.")
                return True
        except Exception as e:
            logger.warning(f"Direct Mumbai navigation notice: {e}")

        # Check if Hindi edition was loaded
        if edition_status.get('isHindi'):
            logger.warning("🚫 Detected Hindi edition of Business Standard. Strictly skipping Hindi edition as requested.")
            raise BusinessStandardEditionNotAvailable("Business Standard English (Mumbai) edition is not available today. Skipped Hindi edition. Token is authenticated.")

        logger.warning("⚠️ Business Standard English - Mumbai edition was not found on the ePaper platform.")
        raise BusinessStandardEditionNotAvailable("Business Standard English (Mumbai) edition not available on platform. Token is authenticated.")

    def download_from_zip(self, zip_path_or_url: str) -> Path:
        """Extracts and merges all page PDFs from a Business Standard single zipped PDF edition."""
        # Strictly reject Hindi zip archives
        if "hindi" in zip_path_or_url.lower():
            logger.warning("🚫 Rejected Hindi zip edition. Token authenticated, but English-Mumbai required.")
            raise BusinessStandardEditionNotAvailable("Business Standard zip archive is for Hindi edition. Skipped Hindi edition. Token is authenticated.")

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

    def extract_articles_from_reader(self, page) -> List[dict]:
        """
        Extracts structured articles from the dedicated Articles side-panel across all edition pages.
        Directly queries the left-side 'Articles' list shown in the reader interface.
        """
        logger.info("Extracting structured articles from Business Standard dedicated Articles section...")
        articles_data = []
        try:
            # Switch to Text or ensure Articles panel is active
            page.evaluate('''() => {
                const textBtn = Array.from(document.querySelectorAll('button, a, div, li')).find(el => (el.innerText || el.textContent || '').trim().toLowerCase() === 'text');
                if (textBtn) { try { textBtn.click(); } catch(e) {} }
            }''')
            page.wait_for_timeout(2000)

            # Discover total pages
            total_pages = page.evaluate('''() => {
                const pageEls = document.querySelectorAll('.page-thumb, .tmb-lst a, [data-pageno], option[value*="page"], .page-dropdown option');
                return Math.max(pageEls.length, 1);
            }''')

            logger.info(f"Scanning {total_pages} pages for dedicated structured articles...")

            for p_num in range(1, min(total_pages + 1, 37)):
                page.evaluate(f'''(p) => {{
                    if (window.goToPage) window.goToPage(p);
                    else if (window.location.hash !== '#' + p) window.location.hash = '#' + p;
                }}''', p_num)
                page.wait_for_timeout(1000)

                page_articles = page.evaluate(r'''(p) => {
                    const items = [];
                    const artElements = document.querySelectorAll('.article_list li, .articles-list a, .art-list a, .story-item, [data-story], [data-artid], .articles a, .article-title, .articles li, .article-list a, div[class*="article"] a');
                    artElements.forEach(el => {
                        const title = (el.innerText || el.textContent || '').trim();
                        const id = el.getAttribute('data-story') || el.getAttribute('data-artid') || el.id || '';
                        if (title && title.length > 5 && !/^article \d+$/i.test(title)) {
                            items.push({ headline: title, page: 'BS (Page ' + p + ')', id });
                        }
                    });
                    return items;
                }''', p_num)

                for art in page_articles:
                    if not any(a['headline'].lower() == art['headline'].lower() for a in articles_data):
                        articles_data.append(art)

            logger.info(f"✅ Extracted {len(articles_data)} unique structured articles from Business Standard Articles section.")
        except Exception as e:
            logger.warning(f"Notice: Articles panel extraction: {e}")

        return articles_data

    def download_full_epaper(
        self,
        epaper_url: str = "https://epaper.business-standard.com/bs_new/index.php?rt=main/mainpage#1",
        storage_state_file: str = "bs_storage_state.json"
    ) -> Path:
        """
        Launches Playwright subscriber session to download all 1-36 pages or full zipped edition.
        Uses authenticated storage state or credentials.
        Raises BusinessStandardSessionError if authentication or session fails.
        """
        state_path = Path(storage_state_file)
        if not state_path.exists() or state_path.stat().st_size < 50:
            # 1. Attempt to fetch latest live session from Cloudflare R2 (synced via website/bookmarklet)
            try:
                r2_session_url = f"{config.r2_public_url.rstrip('/')}/sessions/bs_storage_state.json"
                r = requests.get(r2_session_url, timeout=10)
                if r.ok and len(r.content) > 50:
                    state_path.write_bytes(r.content)
                    logger.info(f"✅ Successfully fetched live Business Standard session from Cloudflare R2 ({len(r.content)} bytes).")
            except Exception as e:
                logger.debug(f"Notice: Could not fetch session from Cloudflare R2: {e}")

            # 2. Attempt to restore from BS_STORAGE_STATE_BASE64 environment variable
            if not state_path.exists():
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

        bs_email = (os.environ.get("BS_EMAIL") or os.environ.get("BS_USERNAME", "")).strip()
        bs_password = os.environ.get("BS_PASSWORD", "").strip()

        if not state_path.exists() and not (bs_email and bs_password):
            error_msg = (
                "❌ CRITICAL SESSION FAILURE: Neither 'BS_STORAGE_STATE_BASE64' nor credentials "
                "('BS_USERNAME' & 'BS_PASSWORD') were found in environment variables / GitHub Secrets."
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
            context_kwargs = {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "viewport": {"width": 1920, "height": 1080},
                "accept_downloads": True
            }
            if state_path.exists():
                context_kwargs["storage_state"] = str(state_path)

            context = browser.new_context(**context_kwargs)
            page = context.new_page()

            try:
                # Prime session on root domain first to ensure SSO cookies propagate to epaper sub-domain
                try:
                    logger.info("Priming subscriber session on business-standard.com...")
                    page.goto("https://www.business-standard.com", timeout=30000, wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)
                except Exception as e:
                    logger.warning(f"Root domain warmup notice: {e}")

                # If no storage state, attempt login
                if not state_path.exists() and bs_email and bs_password:
                    logger.info("No storage state found. Attempting credential login...")
                    try:
                        page.goto("https://www.business-standard.com/sso-login", timeout=30000, wait_until="domcontentloaded")
                        page.wait_for_timeout(2000)
                        email_el = page.wait_for_selector('input[type="email"], input[name="email"], #email', timeout=10000)
                        if email_el:
                            email_el.fill(bs_email)
                        pass_el = page.wait_for_selector('input[type="password"], input[name="password"], #password', timeout=10000)
                        if pass_el:
                            pass_el.fill(bs_password)
                        submit_el = page.wait_for_selector('button[type="submit"], input[type="submit"], button:has-text("Sign In"), button:has-text("Login")', timeout=10000)
                        if submit_el:
                            submit_el.click()
                            page.wait_for_timeout(6000)
                    except Exception as auth_err:
                        logger.warning(f"Credential login notice: {auth_err}")

                # 2. Navigate to ePaper reader
                logger.info(f"Navigating to Business Standard ePaper reader: {epaper_url}")
                page.goto(epaper_url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)

                current_url = page.url
                page_title = page.title()

                # Explicitly detect authentication failure or redirect to login/sso
                if "sso-login" in current_url or "login" in current_url.lower() or "access denied" in page_title.lower():
                    error_msg = (
                        f"❌ SUBSCRIBER AUTHENTICATION FAILED: Redirected to login / access denied. "
                        f"(URL: {current_url}, Title: '{page_title}'). "
                        "Please verify that 'BS_USERNAME' and 'BS_PASSWORD' secrets are correct."
                    )
                    logger.error(error_msg)
                    raise BusinessStandardSessionError(error_msg)

                # 1. Verify and Select English - Mumbai Edition (Strict requirement)
                self._ensure_english_mumbai_edition(page)

                # 2. Trigger Read Offline Modal
                logger.info("Opening Business Standard Read Offline edition download modal...")
                try:
                    readoff_btn = page.wait_for_selector('.readoffline, button[title="Read offline"], img[src*="read-off"]', timeout=15000)
                    if readoff_btn:
                        readoff_btn.click()
                except Exception:
                    page.evaluate('() => { const b = document.querySelector(".readoffline, button[title=\'Read offline\'], img[src*=\'read-off\']"); if (b) b.click(); }')
                page.wait_for_timeout(3000)

                # 3. Select Full Edition Download
                logger.info("Triggering full edition download action...")
                try:
                    full_down = page.wait_for_selector('a.editionall, .fulleditiondown a, .fulleditiondown, .sectiondownlink', timeout=10000)
                    if full_down:
                        full_down.click()
                except Exception:
                    page.evaluate('() => { const b = document.querySelector("a.editionall, .fulleditiondown a, .fulleditiondown, .sectiondownlink"); if (b) b.click(); }')
                page.wait_for_timeout(2000)

                # 4. Confirm Download in Modal & Intercept Download
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
                    if "hindi" in download.suggested_filename.lower():
                        logger.warning("🚫 Download stream returned Hindi edition. Aborting and skipping Hindi edition.")
                        raise BusinessStandardEditionNotAvailable("Business Standard download archive is Hindi edition. Skipped Hindi edition. English (Mumbai) version not available (Token authenticated).")

                    download_path = self.download_dir / download.suggested_filename
                    download.save_as(str(download_path))
                    logger.info(f"Downloaded full edition archive: {download_path} ({download_path.stat().st_size / (1024*1024):.2f} MB)")
                except BusinessStandardEditionNotAvailable:
                    raise
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

                # 5. Fallback: Page-by-Page Single Page Download & Compilation
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

