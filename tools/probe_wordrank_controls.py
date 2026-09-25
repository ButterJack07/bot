import asyncio
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(headless=True); page=await b.new_page(); await page.goto("https://wordrank.net/zh/contexto-unlimited",wait_until="domcontentloaded"); await page.wait_for_timeout(1500); open("tools/wordrank_controls.txt","w",encoding="utf-8").write((await page.locator("body").inner_text()).split("什么是")[0]+"
buttons="+repr(await page.locator("button").evaluate_all("els => els.map(e => ({text:e.innerText,html:e.outerHTML}))"))); await b.close()
asyncio.run(main())
