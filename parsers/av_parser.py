from datetime import datetime
from typing import Optional

from config import NOT_GENERATION_URL
from parsers.base_parser import BasicParser
from database.database_service import DataBaseService


class AVParser(BasicParser):
    def __init__(self):
        super().__init__()
        self.brand: Optional[str] = None
        self._db: DataBaseService = DataBaseService()
        self.brand_id: Optional[int] = None
        self.model_id: Optional[int] = None
        self.generation_id: Optional[int] = None
        self.stop_update: bool = False

    async def run_parser(self, brand: str):
        self.brand = brand.lower()
        await self._db.create_tables()
        await self.get_session()
        await self.get_models()
        await self.close_session()
        return True

    async def get_models(self):
        brand = await self.get_json(data=self.brand)
        for model in brand["seo"]["links"]:
            if self.stop_update:
                return
            data = "/".join(model["url"].split("/")[3:])
            await self.get_generation(model=data)

    async def get_generation(self, model: str):
        generations = await self.get_json(data=model)
        if not generations["seo"]["links"]:
            await self.not_generation(data=generations)

        for generation in generations["seo"]["links"]:
            if self.stop_update:
                return
            years = generation["label"]
            data = "/".join(generation["url"].split("/")[3:])
            await self.get_low_price(generation=data, years=years)

    async def get_low_price(self, generation: str, years: str | None):
        current_curse = await self.get_current_curse()
        data = await self.get_json(data=generation)
        price_min = (
            float(data["seo"]["microMarkup"]["offers"]["lowPrice"]) / current_curse
        )
        price_max = (
            float(data["seo"]["microMarkup"]["offers"]["highPrice"]) / current_curse
        )
        brand = data["metadata"]["brandSlug"]
        model = data["metadata"]["modelSlug"]
        generation = data["metadata"]["generationSlug"]
        years_from = years.split(",")[-1].split("-")[0].strip()
        years_to = (
            years.split(",")[-1].split("-")[1].strip()
            if years.split(",")[-1].split("-")[1].strip() != "..."
            else 2025
        )

        self.brand_id = data["metadata"]["brandId"]
        self.model_id = data["metadata"]["modelId"]
        self.generation_id = data["metadata"]["generationId"]
        average_price, count_cars, _ = await self.get_average_price()

        car_data = {
            "brand": str(brand).lower(),
            "model": str(model).lower(),
            "generation": str(generation),
            "year_from": int(years_from),
            "year_to": int(years_to),
            "price_min": float(price_min),
            "price_max": float(price_max),
            "average_price": float(average_price),
            "count_cars": int(count_cars),
            "updated_at": datetime.now(),
        }

        await self._db.save_car_data(car_data=car_data)
        self.logger.info(
            f"Record successfully added to the database: {brand.upper()} {model} "
            f"(Production Years: {years_from} – {years_to})"
        )

    async def get_average_price(self):
        cars = await self.get_cars(
            brand_id=self.brand_id,
            model_id=self.model_id,
            generation_id=self.generation_id,
        )
        prices = []
        for car in cars:
            cost = [cost["price"]["usd"]["amount"] for cost in car["adverts"]]
            prices.extend(cost)
        average = sum(prices) / len(prices)
        return average, len(prices), cars

    async def not_generation(self, data: dict):
        current_curse = await self.get_current_curse()

        price_min = (
            float(data["seo"]["microMarkup"]["offers"]["lowPrice"]) / current_curse
        )
        price_max = (
            float(data["seo"]["microMarkup"]["offers"]["highPrice"]) / current_curse
        )
        brand = data["metadata"]["brandSlug"]
        model = data["metadata"]["modelSlug"]
        generation = "without generation"

        self.brand_id = data["metadata"]["brandId"]
        self.model_id = data["metadata"]["modelId"]

        average_price, count_cars, cars = await self.get_average_price()
        years = [year["metadata"]["year"] for car in cars for year in car["adverts"]]
        years_from, years_to = min(years), max(years)

        car_data = {
            "brand": str(brand).lower(),
            "model": str(model).lower(),
            "generation": str(generation),
            "year_from": int(years_from),
            "year_to": int(years_to),
            "price_min": float(price_min),
            "price_max": float(price_max),
            "average_price": float(average_price),
            "count_cars": int(count_cars),
            "updated_at": datetime.now(),
        }
        await self._db.save_car_data(car_data=car_data)
        self.logger.info(
            f"Record successfully added to the database: {brand.upper()} {model} "
            f"(Production Years: {years_from} – {years_to})"
        )
