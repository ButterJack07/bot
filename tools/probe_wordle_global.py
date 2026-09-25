import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://wordle.global/zh/unlimited", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2500)
        skip = page.get_by_text("跳到游戏", exact=True)
        if await skip.count():
            await skip.evaluate("element => element.click()")
            await page.wait_for_timeout(500)
        result = (
            f"inputs={await page.locator('input,textarea,[contenteditable=true]').count()}\n"
            f"buttons={repr(await page.locator('button').all_inner_texts())}\n"
            f"editable={repr(await page.locator('[contenteditable=true]').evaluate_all('els => els.map(e => e.outerHTML)'))}\n"
            f"body={repr((await page.locator('body').inner_text())[:2500])}"
        )
        Path("tools/wordle_global_probe.txt").write_text(result, encoding="utf-8")
        await browser.close()


asyncio.run(main())
