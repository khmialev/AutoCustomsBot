import asyncio
from urllib.parse import urlencode

from parsers.base_parser import BasicParser


class AVStatistic(BasicParser):
    # todo есть косяк в том что иногда ничего нет на av с этими параметрми 7ка 2020 года 3.0 бенз, может лучше брать без года??? хз надо подумать
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.av.by/offer-types/cars"
        self.brand_path = "/catalog/brand-items"
        self.model_path = "/catalog/brand-items/{brand_id}/models"
        self.generation_path = (
            "/catalog/brand-items/{brand_id}/models/{model_id}/generations"
        )
        self.statistic_path = "/price-statistics"

    async def build_url(self, path: str, query: dict = None, **kwargs) -> str:
        url = self.base_url + path.format(**kwargs)
        if query:
            url += "?" + urlencode(query)
        return url

    async def get_data(self, url):
        await self.get_session()
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        }
        async with self._session.get(url=url, headers=headers) as r:
            data = await r.json()
            await self.close_session()
            return data

    async def run(
        self,
        brand: str = "bmw",
        model: str = "7-seriya",
        year: str = "2020",
        engine_capacity: str = "3000",
        engine_type: str = "1",  # 1 - бензин, 5 -дизель
    ):
        brand_id = await self.get_brand(brand)
        model_id = await self.get_model(brand_id=str(brand_id), model=model)
        generation_id = await self.get_generation(
            brand_id=str(brand_id), model_id=str(model_id), year=year
        )
        # можно еще взять мотор и типу(диз/бенз) и сделать статистику по году + объему + тип двигателя
        statistic = await self.get_statistic(
            year, brand_id, model_id, generation_id, engine_capacity, engine_type
        )
        print(statistic)

    async def get_brand(self, brand):
        data = await self.get_data(url=self.base_url + self.brand_path)
        brands_map = {item["slug"]: item["id"] for item in data}
        return brands_map.get(brand, None)

    async def get_model(self, brand_id: str, model: str):
        url = await self.build_url(self.model_path, brand_id=brand_id)

        data = await self.get_data(url=url)
        brands_map = {item["slug"]: item["id"] for item in data}
        return brands_map.get(model, None)

    async def get_generation(self, brand_id: str, model_id: str, year: str):
        url = await self.build_url(
            self.generation_path, brand_id=brand_id, model_id=model_id
        )
        data = await self.get_data(url=url)

        year = int(year)
        for item in data:
            year_from = item.get("yearFrom", 0)
            year_to = item.get("yearTo")  # может быть None
            if year_from <= year and (year_to is None or year <= year_to):
                return item["id"]

        return None  # если не найдено

    async def get_statistic(
        self, year, brand_id, model_id, generation_id, engine_capacity, engine_type
    ):
        url = await self.build_url(
            self.statistic_path,
            query={
                "brand": brand_id,
                "model": model_id,
                "generation": generation_id,
                "year": year,
                "engine_capacity": engine_capacity,
                "engine_type": engine_type,
                "available_year": year,
            },
        )
        return await self.get_data(url=url)


a = AVStatistic()
asyncio.run(a.run())
