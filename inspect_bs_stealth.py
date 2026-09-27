import asyncio
from playwright.async_api import async_playwright

async def inspect_stealth():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        url = "https://www.business-standard.com/sso-login"
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        title = await page.title()
        print(f"Title: {title}")
        print(f"URL: {page.url}")

        # Look for Google Sign-In button or iframe
        iframes = page.frames
        print(f"Total frames on page: {len(iframes)}")

        buttons = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('button, a, div[id*="google"], iframe[src*="google"]'))
                .map(el => ({
                    tag: el.tagName,
                    text: (el.innerText || el.textContent || '').trim(),
                    id: el.id,
                    className: el.className,
                    src: el.src || ''
                }));
        }""")

        print("Interactive Elements found on SSO Login:")
        for b in buttons:
            if any(k in (b['text'] + b['id'] + b['className'] + b['src']).lower() for k in ['google', 'sign', 'login', 'g_id']):
                print(b)

        await page.screenshot(path="bs_sso_screenshot.png")
        print("Saved screenshot to bs_sso_screenshot.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_stealth())
