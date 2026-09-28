"""
Business Standard ePaper One-Time Login Helper
Uses a persistent browser profile to store Google SSO and ePaper session credentials.
"""

import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR = Path("bs_browser_profile").resolve()
TARGET_URL = "https://epaper.business-standard.com/bs_new/index.php?rt=main/mainpage#1"

async def setup_login():
    print("=" * 68)
    print(" BUSINESS STANDARD GOOGLE SSO LOGIN SETUP (PERSISTENT PROFILE)")
    print("=" * 68)
    print("Opening browser with persistent profile...")
    print("1. Log in with your Google Email / Credentials.")
    print("2. Ensure the ePaper reader edition (Page 1) is fully visible.")
    print("3. Return to this terminal and press ENTER.")
    print("=" * 68)

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.pages[0] if context.pages else await context.new_page()

        try:
            await page.goto(TARGET_URL, wait_until="domcontentloaded")
        except Exception as e:
            print(f"Navigation notice: {e}")

        print("\n[Awaiting Login] Please complete your Google SSO login in the browser...")
        input("\n>>> Press ENTER AFTER the ePaper reader edition is loaded on your screen <<< ")

        # Also save storage state JSON backup
        await context.storage_state(path="bs_storage_state.json")
        
        # Encode to Base64 for GitHub Actions Secret
        import base64
        import subprocess
        with open("bs_storage_state.json", "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")
        
        with open("bs_storage_state_base64.txt", "w", encoding="utf-8") as f:
            f.write(b64_str)

        # Copy to clipboard on macOS
        try:
            subprocess.run(["pbcopy"], input=b64_str.encode("utf-8"), check=True)
            copied_msg = "📋 Fresh Base64 secret COPIED TO CLIPBOARD automatically!"
        except Exception:
            copied_msg = "Base64 token written to 'bs_storage_state_base64.txt'"

        print("\n" + "=" * 68)
        print("✅ BUSINESS STANDARD SESSION CAPTURED SUCCESSFULLY!")
        print("=" * 68)
        print(f"{copied_msg}")
        print("\n👉 ACTION: Update your GitHub Action Secret:")
        print("   1. Go to: GitHub Repo -> Settings -> Secrets and variables -> Actions")
        print("   2. Update 'BS_STORAGE_STATE_BASE64' with the copied token (Cmd+V).")
        print("   3. Click 'Update secret'.")
        print("=" * 68 + "\n")

        await context.close()

if __name__ == "__main__":
    asyncio.run(setup_login())

