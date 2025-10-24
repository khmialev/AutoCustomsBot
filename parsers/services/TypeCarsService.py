import asyncio
import json

import requests
from fake_useragent import UserAgent

from src.bot.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger()
settings = get_settings()


class FormedCarsData:
    ua = UserAgent().random
    parsed_data: json = {}
    headers = {
        'sec-ch-ua-full-version-list': '"Google Chrome";v="141.0.7390.108", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.108"',
        'sec-ch-ua-platform': '"macOS"',
        'Referer': 'https://bid.cars/ru/search/results?search-type=filters&status=All&type=Automobile&make=All&model=All&year-from=1900&year-to=2026&auction-type=All',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-arch': '"arm"',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-full-version': '"141.0.7390.108"',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': ua,
        'sec-ch-ua-platform-version': '"26.0.1"',
        }

    async def get_data(self):
        response = requests.get(settings.BIDCARS_TIPS, headers=self.headers)
        data = response.content
        decoded = data.decode('utf-8')
        self.parsed_data = json.loads(decoded)


    async def formed_data(self):
        await self.get_data()
        result = {}
        for car in self.parsed_data:
            make = car.get("make")
            model = car.get("model")

            if not make or not model:
                continue

            if make not in result:
                result[make] = {}

            result[make][model] = {
                "generations": car.get("generations", []),
            }

        with open("../cars_structured.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info('success if create json file for car type')

formed_data = FormedCarsData().formed_data()
asyncio.run(formed_data)