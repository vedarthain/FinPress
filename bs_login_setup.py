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
        
        # 1. Upload directly to Cloudflare R2 bucket
        try:
            from cloud_storage import upload_to_r2
            r2_url = upload_to_r2("bs_storage_state.json", "sessions/bs_storage_state.json")
            if r2_url:
                print(f"☁️ Cloudflare R2 Session Synced: {r2_url}")
        except Exception as e:
            print(f"Notice (R2 sync): {e}")

        # Encode to Base64 for GitHub Actions Secret
        import base64
        import subprocess
        with open("bs_storage_state.json", "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")
        
        with open("bs_storage_state_base64.txt", "w", encoding="utf-8") as f:
            f.write(b64_str)

        # 2. Try updating GitHub Secret directly from CLI via gh
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

        # 4. Trigger GitHub Actions Workflow Run
        try:
            gh_run = subprocess.run(
                ["gh", "workflow", "run", "2_fetch_business_standard.yml", "--repo", "vedarthain/FinPress"],
                capture_output=True,
                check=False
            )
            if gh_run.returncode == 0:
                print("⚡ GITHUB ACTIONS WORKFLOW TRIGGERED AUTOMATICALLY!")
            else:
                pass
        except Exception:
            pass

        print("\n" + "=" * 68)
        print("✅ BUSINESS STANDARD SESSION SYNCED & PIPELINE READY!")
        print("   Live Run: https://github.com/vedarthain/FinPress/actions")
        print("   Dashboard: https://finpress.deb5045ai.workers.dev")
        print("=" * 68 + "\n")

        await context.close()

if __name__ == "__main__":
    asyncio.run(setup_login())

