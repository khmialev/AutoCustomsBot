import asyncio
from datetime import datetime
from fake_useragent import UserAgent

from docker.backend.config import USD_URL, AV_PAGE_URL
from parsers.heders.AvHeaders import AV_HEADERS
from parsers.models.CarModel import AvStatisticCar
from parsers.services.AioHttpService import aiohttp_service
from parsers.urls.urls import AV_BASE_URL
from src.utils.logger import get_logger

logger = get_logger()


class AvStatistic:
    def __init__(self):
        self.parms = {
            "headers": {**AV_HEADERS, "User-Agent": UserAgent().random}
        }

    async def run_parser(self, brand: str, model: str, year: str):
        url = f"{AV_BASE_URL}{brand}"
        brands = await aiohttp_service.get_json_data(url=url, **self.parms)
        if brands:
            for brand in brands["seo"]["links"]:
                path = "/".join(brand["url"].split("/")[3:])
                m = path.split("/")[-1]
                if m == model:
                    return await self.get_generation(model=path, year=year)
        logger.warning("Dont have brands")
        return None

    async def get_generation(self, model: str, year: str):
        cars = []
        url = f"{AV_BASE_URL}{model}"
        generations = await aiohttp_service.get_json_data(url=url, **self.parms)
        if not generations["seo"]["links"]:
            cars.append(await self.get_low_price(data=generations, year=year))

        for generation in generations["seo"]["links"]:
            years = generation["label"].split(",")[-1].split("-")
            year_from = int(years[0].strip())
            year_to = (
                datetime.now().year
                if years[1] == "..."
                else int(years[1].strip())
            )

            year_int = int(year)
            if year_from and year_to and not (year_from <= year_int <= year_to):
                continue

            data = "/".join(generation["url"].split("/")[3:])
            cars.append(await self.get_low_price(data=data, year=year))
        return cars

    async def get_low_price(self, data: str, year):
        url = f"{AV_BASE_URL}{data}"
        current_curse_json = await aiohttp_service.get_json_data(url=USD_URL)
        current_curse = float(current_curse_json["Cur_OfficialRate"])
        data = await aiohttp_service.get_json_data(url=url, **self.parms)
        price_min = (
            float(data["seo"]["microMarkup"]["offers"]["lowPrice"])
            / current_curse
        )
        price_max = (
            float(data["seo"]["microMarkup"]["offers"]["highPrice"])
            / current_curse
        )
        brand = data["metadata"]["brandSlug"]
        model = data["metadata"]["modelSlug"]
        generation = data["metadata"]["generationSlug"]

        brand_id = data["metadata"]["brandId"]
        model_id = data["metadata"]["modelId"]
        try:
            generation_id = data["metadata"]["generationId"]
        except:
            generation_id = None
        average_price, count_cars = await self.get_average_price(
            brand_id=brand_id, model_id=model_id, generation_id=generation_id
        )
        await aiohttp_service.close_session()
        return AvStatisticCar(
            brand=str(brand),
            model=str(model),
            generation=str(generation),
            year=str(year),
            price_min=float(price_min),
            price_max=float(price_max),
            average_price=float(average_price),
            count_cars=int(count_cars),
        )

    async def get_average_price(self, brand_id, model_id, generation_id=None):
        generation = {"name": "generation", "value": generation_id}
        page = 1
        cars = []

        while True:
            json_data = {
                "page": page,
                "properties": [
                    {
                        "name": "brands",
                        "property": 6,
                        "value": [
                            [
                                {"name": "brand", "value": brand_id},
                                {"name": "model", "value": model_id},
                            ],
                        ],
                    },
                    {
                        "name": "price_currency",
                    },
                ],
                "sorting": 1,
            }
            if generation_id:
                json_data["properties"][0]["value"][0].append(generation)
            data = await aiohttp_service.post_data(
                url=AV_PAGE_URL, **self.parms, json_data=json_data, cookies=None
            )

            cars.append(data)

            page_count = data.get("pageCount", 1)
            if page >= page_count:
                break
            page += 1

        prices = []
        prices.extend(
            [
                cost["price"]["usd"]["amount"]
                for car in cars
                for cost in car["adverts"]
            ]
        )

        average = sum(prices) / len(prices)
        return average, len(prices)


av_statistic = AvStatistic()
asyncio.run(av_statistic.run_parser(brand="bmw", model="3-seriya", year="2020"))
