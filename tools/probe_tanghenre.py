import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        requests = []
        page.on("request", lambda request: requests.append((request.method, request.url, request.post_data)))
        await page.goto("https://www.tanghenre.com/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        print("inputs", await page.locator("input,textarea").count())
        links = await page.locator("a").evaluate_all("els => els.map(e => ({text:e.innerText, href:e.href})).filter(x => x.href.includes('/tang/')).slice(0, 3)")
        print("links", links)
        print("api", [item for item in requests if any(key in item[1] for key in ("api", "trpc", "chat", "guess"))])
        await browser.close()


asyncio.run(main())
