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

        # 1. Try updating GitHub Secret directly from CLI via gh
        gh_success = False
        try:
            res = subprocess.run(
                ["gh", "secret", "set", "BS_STORAGE_STATE_BASE64", "--repo", "vedarthain/FinPress"],
                input=b64_str.encode("utf-8"),
                capture_output=True,
                check=False
            )
            if res.returncode == 0:
                gh_success = True
        except Exception:
            pass

        # 2. Copy to clipboard on macOS as backup
        try:
            subprocess.run(["pbcopy"], input=b64_str.encode("utf-8"), check=True)
            copied_msg = "📋 Token copied to macOS clipboard."
        except Exception:
            copied_msg = "Token written to 'bs_storage_state_base64.txt'."

        print("\n" + "=" * 68)
        print("✅ BUSINESS STANDARD SESSION CAPTURED SUCCESSFULLY!")
        print("=" * 68)
        
        if gh_success:
            print("🚀 GITHUB SECRET 'BS_STORAGE_STATE_BASE64' UPDATED AUTOMATICALLY VIA CLI!")
            print("   You do not need to do anything manually. The cloud is in sync!")
        else:
            print(f"{copied_msg}")
            print("\n👉 To update GitHub Secret in 1-click from CLI:")
            print("   1. Run once:  gh auth login")
            print("   2. Then run:  gh secret set BS_STORAGE_STATE_BASE64 < bs_storage_state_base64.txt --repo vedarthain/FinPress")
        print("=" * 68 + "\n")

        await context.close()

if __name__ == "__main__":
    asyncio.run(setup_login())

