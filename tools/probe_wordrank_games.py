import asyncio
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(headless=True)
  page=await b.new_page()
  for i in range(3):
   await page.goto("https://wordrank.net/zh/contexto-unlimited",wait_until="domcontentloaded",timeout=20000)
   await page.wait_for_timeout(1200)
   open(f"tools/wordrank_game_{i}.txt","w",encoding="utf-8").write(await page.locator("body").inner_text())
  await b.close()
asyncio.run(main())
