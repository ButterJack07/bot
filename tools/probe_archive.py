import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://wordrank.net/zh/daily/130", wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(2500)
        result = (
            f"inputs={await page.locator('input:not([type=hidden]),textarea').count()}\n"
            f"menus={repr(await page.locator('button').all_inner_texts())}\n"
            f"body={repr((await page.locator('body').inner_text())[:1500])}"
        )
        Path("tools/archive_probe.txt").write_text(result, encoding="utf-8")
        await browser.close()


asyncio.run(main())
