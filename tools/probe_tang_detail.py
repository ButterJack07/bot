import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        requests = []
        page.on("request", lambda request: requests.append((request.method, request.url, request.post_data)))
        await page.goto("https://tanghenre.com/tang/%E6%B5%B7%E9%BE%9F%E6%B1%A4%E7%9A%84%E6%95%85%E4%BA%8B", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2500)
        result = (
            repr(await page.locator("button").all_inner_texts())
            + "\ninputs=" + str(await page.locator("input,textarea,[contenteditable=true]").count())
            + "\ncontrols=" + repr(await page.locator("input,textarea,[contenteditable=true]").evaluate_all("els => els.map(e => ({tag:e.tagName,placeholder:e.placeholder,aria:e.getAttribute('aria-label'),text:e.innerText}))"))
            + "\nbody=" + repr((await page.locator("body").inner_text())[-3000:])
        )
        editor = page.locator("[contenteditable=true]").first
        if await editor.count():
            await editor.fill("他以前喝过海龟汤吗？")
            await editor.press("Enter")
            await page.wait_for_timeout(1200)
            result += "\nafter=" + repr((await page.locator("body").inner_text())[-1200:])
            result += "\npost_api=" + repr([item for item in requests if item[0] == "POST"])
        Path("tools/tang_detail.txt").write_text(result, encoding="utf-8")
        print([item for item in requests if "/api/" in item[1]])
        await browser.close()


asyncio.run(main())
