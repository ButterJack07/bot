import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://wordrank.net/zh/contexto-unlimited", wait_until="domcontentloaded")
        await page.wait_for_timeout(1500)
        field=page.locator("input:not([type=hidden]),textarea").last
        await field.fill("苹果")
        await field.press("Enter")
        await page.wait_for_timeout(500)
        controls = await page.locator("button").evaluate_all("els => els.map(e => ({text:e.innerText, html:e.outerHTML}))")
        await page.get_by_role("button", name="玩").first.click()
        await page.wait_for_timeout(300)
        menus = await page.locator("[role='menu'], [role='menuitem'], a").evaluate_all("els => els.map(e => ({text:e.innerText, href:e.href || ''})).filter(x => x.text)")
        await page.get_by_role("button", name=re.compile("打开菜单")).last.click()
        await page.get_by_text("放弃 / 看答案", exact=True).last.click()
        await page.wait_for_timeout(500)
        body = await page.locator("body").inner_text()
        storage = await page.evaluate("Object.entries(localStorage)")
        scripts = await page.locator("script[src]").evaluate_all("els => els.map(e => e.src)")
        options = page.get_by_role("button", name=re.compile("打开菜单"))
        if await options.count():
            await options.last.click()
            await page.wait_for_timeout(300)
        option_menu = await page.locator("[role='menuitem'], button, [role='button']").evaluate_all("els => els.map(e => e.innerText || e.getAttribute('aria-label')).filter(Boolean)")
        Path("tools/wordrank_inspect.txt").write_text(repr(controls) + "\nmenus=" + repr(menus) + "\nstorage=" + repr(storage) + "\nscripts=" + repr(scripts) + "\noptions=" + repr(option_menu) + "\n" + body[:2500], encoding="utf-8")
        await browser.close()


asyncio.run(main())
