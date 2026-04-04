import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        content = await page.evaluate("document.getElementById('chat-content').innerText")
        print("CONTENT:", content)

asyncio.run(main())
