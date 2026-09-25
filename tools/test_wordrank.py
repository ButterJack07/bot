import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        requests = []
        page.on("request", lambda request: requests.append((request.method, request.url, request.post_data)))
        await page.goto("https://wordrank.net/zh/contexto-unlimited", wait_until="networkidle")
        report = [
            f"title={await page.title()}",
            f"inputs={await page.locator('input:not([type=hidden]),textarea').count()}",
            f"buttons={repr(await page.locator('button').all_inner_texts())}",
            f"body={repr((await page.locator('body').inner_text())[:3000])}",
        ]
        field = page.locator("input:not([type=hidden]),textarea").last
        report.append(f"input_attrs={await field.evaluate('(element) => ({placeholder: element.placeholder, type: element.type, aria: element.getAttribute(\"aria-label\")})')}")
        await field.fill("苹果")
        await field.press("Enter")
        await page.wait_for_timeout(1200)
        report.append(f"after_guess={repr((await page.locator('body').inner_text())[:1800])}")
        report.append(f"requests={repr([item for item in requests if '/api/' in item[1] or 'guess' in item[1]])}")
        report.append(f"storage={await page.evaluate("Object.entries(localStorage)")}")
        Path("tools/wordrank_probe.txt").write_text("\n".join(report), encoding="utf-8")
        await browser.close()


asyncio.run(main())
