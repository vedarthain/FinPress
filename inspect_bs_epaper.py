import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)

async def inspect_bs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        urls_to_test = [
            "https://epaper.business-standard.com/",
            "https://www.business-standard.com/epaper"
        ]

        for url in urls_to_test:
            print(f"\n--- Testing URL: {url} ---")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(3000)
                title = await page.title()
                print(f"Title: {title}")
                print(f"Final URL: {page.url}")

                # Find Google SSO, login buttons, download links
                elements = await page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a, button, input[type="button"], div[class*="login"], iframe'))
                        .map(el => ({
                            tag: el.tagName,
                            text: (el.innerText || el.textContent || '').trim().slice(0, 80),
                            href: el.href || '',
                            src: el.src || '',
                            cls: el.className,
                            id: el.id
                        }))
                        .filter(item => {
                            const str = (item.text + item.href + item.src + item.cls + item.id).lower ? 
                                        (item.text + item.href + item.src + item.cls + item.id).toLowerCase() : '';
                            return str.includes('google') || str.includes('login') || str.includes('sign') || str.includes('pdf') || str.includes('download') || str.includes('epaper');
                        });
                }""")

                print(f"Found {len(elements)} relevant login/download elements:")
                for e in elements[:15]:
                    print(e)
            except Exception as err:
                print(f"Error accessing {url}: {err}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_bs())
