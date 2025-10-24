import json
from playwright.async_api import async_playwright, Page
from fake_useragent import UserAgent
from src.bot.settings import get_settings


settings = get_settings()


class PlayWrightManager:
    def __init__(self):
        self.ua = UserAgent()
        self._proxy = settings.get_proxy_config()

    async def _fetch_page(self, url: str, iaai=False) -> Page:
        self._ua = self.ua.random
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True, proxy=self._proxy,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--window-size=1920,1080",
                "--start-maximized",
            ],

        )
        self._context = await self._browser.new_context(
            user_agent=self._ua,
            locale="en-US",
            extra_http_headers={ # можно норм прокинуть
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )
        await self._context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)
        page = await self._context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        if not iaai:
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

    async def get_bidcars_tips(self, url: str):
        page = await self._fetch_page(url)
        raw_body = await page.locator("body").inner_text()
        await self._cleanup()
        return json.loads(raw_body)

    async def get_iaai_car_page(self, url, iaai=False):
        page = await self._fetch_page(url, iaai=iaai)
        html = await page.content()
        await self._cleanup()
        return html


playwright = PlayWrightManager()
