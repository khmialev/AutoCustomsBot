import json
from playwright.async_api import async_playwright, Page
from fake_useragent import UserAgent


class PlayWrightManager:
    def __init__(self):
        self.ua = UserAgent()

    async def _fetch_page(self, url: str) -> Page:
        self._ua = self.ua.random
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._context = await self._browser.new_context(
            user_agent=self._ua,
            locale="en-US",
            # proxy={"server": "http://myproxy:3128"}
        )
        page = await self._context.new_page()
        await page.goto(url, timeout=5000)
        await page.wait_for_load_state("networkidle")
        return page

    async def _cleanup(self):
        await self._browser.close()
        await self._playwright.stop()

    async def get_data_for_copart(self, url: str) -> dict:
        page = await self._fetch_page(url)
        await page.wait_for_selector("pre")
        pre_text = await page.locator("pre").text_content()
        await self._cleanup()
        return json.loads(pre_text)

    async def get_data(self, url: str) -> dict:
        page = await self._fetch_page(url)
        content = await page.content()
        await self._cleanup()
        start = content.find(">{") + 1
        end = content.rfind("}</body>") + 1
        json_str = content[start:end]
        return json.loads(json_str)
