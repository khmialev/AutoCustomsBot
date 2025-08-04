import asyncio
from urllib.parse import urlencode
from fake_useragent import UserAgent
from parsers.models.CarModel import AvAnalyticsCar
from parsers.services.AioHttpService import aiohttp_service
from parsers.urls.urls import (
    AV_STATISTIC_MODEL_URl,
    AV_STATISTIC_GENERATION_URl,
    AV_STATISTIC_BRAND_URl,
    AV_STATISTIC_BASE_URl,
    AV_STATISTIC_PATH,
)


class AvAnalytics:
    def __init__(self) -> None:
        self.parms = {
            "headers": {
                "user-agent": UserAgent().random,
            }
        }

    async def run(
        self,
        brand: str,
        model: str,
        year: str,
        engine_capacity: str,
        engine_type: str,  # 1 - бензин, 5 -дизель
    ):
        brand_id = await self.get_brand(brand)
        model_id = await self.get_model(brand_id=str(brand_id), model=model)
        generation_ids = await self.get_generation(
            brand_id=str(brand_id), model_id=str(model_id), year=year
        )

        return await self.get_statistic(
            year,
            brand_id,
            model_id,
            generation_ids,
            engine_capacity,
            engine_type,
        )

    async def get_brand(self, brand):
        data = await aiohttp_service.get_json_data(
            url=AV_STATISTIC_BRAND_URl, proxy=False, cookies=False, **self.parms
        )
        brands_map = {item["slug"]: item["id"] for item in data}
        return brands_map.get(brand.lower(), None)

    async def get_model(self, brand_id: str, model: str):
        url = AV_STATISTIC_MODEL_URl.format(brand_id=brand_id)
        data = await aiohttp_service.get_json_data(
            url=url, proxy=False, cookies=False, **self.parms
        )
        brands_map = {item["slug"]: item["id"] for item in data}
        return brands_map.get(model.lower(), None)

    async def get_generation(self, brand_id: str, model_id: str, year: str):
        url = AV_STATISTIC_GENERATION_URl.format(
            brand_id=brand_id, model_id=model_id
        )
        data = await aiohttp_service.get_json_data(
            url=url, proxy=False, cookies=False, **self.parms
        )
        year = int(year)
        generations = []
        for item in data:
            year_from = item.get("yearFrom", 0)
            year_to = item.get("yearTo")  # может быть None
            if year_from <= year and (year_to is None or year <= year_to):
                generations.append(item["id"])

        return generations

    async def build_url(self, path: str, query: dict = None, **kwargs) -> str:
        url = AV_STATISTIC_BASE_URl + path.format(**kwargs)
        if query:
            url += "?" + urlencode(query)
        return url

    async def get_statistic(
        self,
        year,
        brand_id,
        model_id,
        generation_ids,
        engine_capacity,
        engine_type,
    ):
        urls = await asyncio.gather(
            *[
                self.build_url(
                    AV_STATISTIC_PATH,
                    query={
                        "brand": brand_id,
                        "model": model_id,
                        "generation": gen,
                        "year": year,
                        "engine_capacity": str(engine_capacity * 1000),
                        "engine_type": engine_type,
                        "available_year": year,
                    },
                )
                for gen in generation_ids
            ]
        )

        responses = await asyncio.gather(
            *[
                aiohttp_service.get_json_data(
                    url=url, proxy=False, cookies=False, **self.parms
                )
                for url in urls
            ]
        )

        return await self.formed_data(responses)

    @staticmethod
    async def formed_data(data_list):
        if not isinstance(data_list, list):
            data_list = [
                data_list
            ]  # оборачиваем в список, если пришёл один объект

        cars = []
        for data in data_list:
            brand = data["title"]["brand"]
            model = data["title"]["model"]
            generation = data["title"]["generation"]
            year = data["title"]["year"]
            average_price = data["mediumPrice"]["priceUsd"]
            average_sell_days = int(
                sum(i["originalDaysOnSale"] for i in data["lastSoldAdverts"])
                / len(data["lastSoldAdverts"])
            )
            car = AvAnalyticsCar(
                brand=brand,
                model=model,
                generation=generation,
                year=year,
                average_price=average_price,
                average_sell_days=average_sell_days,
            )
            cars.append(car)
        return cars


av_analytics = AvAnalytics()
