from config import IAAI_URL
from models.cars import IaaiCar
from parsers.base_parser import BasicParser


class IaaiParser(BasicParser):
    def __init__(self, iaai_url: str):
        super().__init__()
        self.url = iaai_url

    async def get_data(self):
        await self.get_session()
        car_code = self.url.split("/")[-1].split("~")[0]
        iaai_url = f"{IAAI_URL}{car_code}"
        car_data = await self.get_iaai_json(iaai_url=iaai_url)
        if not car_data:
            return False
        brand = car_data["MakeName"]
        model = car_data["ModelName"]
        year = car_data["ModelYear"]
        dirty_engine = await self.get_iaai_engine(iaai_url=self.url)
        if not dirty_engine:
            return False
        engine = float(dirty_engine.split(" ")[0].lower().replace("l", ""))

        if brand == "BMW":
            model: str = f"{model[0]}-seriya"

        await self.close_session()
        return IaaiCar(brand=brand, model=model, year=year, engine=engine)
