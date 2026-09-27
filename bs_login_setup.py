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
        print("\n✅ Session and browser profile saved successfully in 'bs_browser_profile' and 'bs_storage_state.json'!")
        print("Now you can run: python main.py --source business_standard\n")

        await context.close()

if __name__ == "__main__":
    asyncio.run(setup_login())
