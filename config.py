"""
Configuration module for Newspaper PDF Automation & Gemini Analysis Pipeline.
Loads settings from environment variables or .env file.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()


class AppConfig(BaseModel):
    # Newspaper Settings (Defaults to dynamic latest Mumbai edition URL)
    newspaper_url: str = Field(
        default_factory=lambda: os.getenv(
            "NEWSPAPER_URL",
            "https://epaper.financialexpress.com/t/26733/latest/Mumbai"
        )
    )
    newspaper_username: str = Field(
        default_factory=lambda: os.getenv("NEWSPAPER_USERNAME", "")
    )
    newspaper_password: str = Field(
        default_factory=lambda: os.getenv("NEWSPAPER_PASSWORD", "")
    )

    # Selectors tuned for Financial Express & ReadWhere ePaper platforms
    username_selector: str = Field(
        default_factory=lambda: os.getenv(
            "USERNAME_SELECTOR",
            "#email, #username, input[type='email'], input[name='email'], input[name='username']"
        )
    )
    password_selector: str = Field(
        default_factory=lambda: os.getenv(
            "PASSWORD_SELECTOR",
            "#password, input[type='password'], input[name='password']"
        )
    )
    submit_selector: str = Field(
        default_factory=lambda: os.getenv(
            "SUBMIT_SELECTOR",
            "#login-btn, button[type='submit'], input[type='submit'], .login-submit-btn"
        )
    )
    login_trigger_selector: str = Field(
        default_factory=lambda: os.getenv(
            "LOGIN_TRIGGER_SELECTOR",
            ".login-required, .login-link-free, .login-link, .newspaper_v4_login"
        )
    )
    download_trigger_selector: str = Field(
        default_factory=lambda: os.getenv(
            "DOWNLOAD_TRIGGER_SELECTOR",
            "a.download-pdf, #download-icon, .download-pdf, button.download-pdf"
        )
    )
    confirm_download_selector: str = Field(
        default_factory=lambda: os.getenv(
            "CONFIRM_DOWNLOAD_SELECTOR",
            ".confirm-btn, .archive_download-btn, button:has-text('Download PDF'), a:has-text('Download PDF')"
        )
    )

    # Playwright Browser Settings
    headless: bool = Field(
        default_factory=lambda: os.getenv("HEADLESS", "true").lower() == "true"
    )
    browser_timeout_ms: int = Field(
        default_factory=lambda: int(os.getenv("BROWSER_TIMEOUT_MS", "60000"))
    )
    download_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("DOWNLOAD_DIR", "./downloads")).resolve()
    )

    # Gemini API Settings
    gemini_api_key: str = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "")
    )
    gemini_model: str = Field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    )
    pdf_chunk_size: int = Field(
        default_factory=lambda: int(os.getenv("PDF_CHUNK_SIZE", "2"))
    )

    # Daily Schedule Settings
    schedule_time: str = Field(
        default_factory=lambda: os.getenv("SCHEDULE_TIME", "06:00")
    )
    output_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("OUTPUT_DIR", "./reports")).resolve()
    )

    # Cloudflare R2 Storage Settings
    r2_account_id: str = Field(
        default_factory=lambda: os.getenv("R2_ACCOUNT_ID", "")
    )
    r2_access_key_id: str = Field(
        default_factory=lambda: os.getenv("R2_ACCESS_KEY_ID", "")
    )
    r2_secret_access_key: str = Field(
        default_factory=lambda: os.getenv("R2_SECRET_ACCESS_KEY", "")
    )
    r2_bucket_name: str = Field(
        default_factory=lambda: os.getenv("R2_BUCKET_NAME", "")
    )
    r2_public_url: str = Field(
        default_factory=lambda: os.getenv("R2_PUBLIC_URL", "")
    )

    def is_r2_configured(self) -> bool:
        return bool(self.r2_account_id and self.r2_access_key_id and self.r2_secret_access_key and self.r2_bucket_name)

    def validate_api_key(self):
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. Please set GEMINI_API_KEY in .env or environment."
            )

    def ensure_directories(self):
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


config = AppConfig()
