import json
from playwright.async_api import async_playwright
from fake_useragent import UserAgent


class PlayRightManager:
    # todo прокси прокинуть надо бы
    async def get_data(self, url: str) -> str:
        ua = UserAgent().random
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=ua,
                locale="en-US",
            )
            page = await context.new_page()

            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("networkidle")

            content = await page.content()
            await browser.close()
            start = content.find(">{") + 1
            end = content.rfind("}</body>") + 1
            json_str = content[start:end]

            data = json.loads(json_str)
            return data
