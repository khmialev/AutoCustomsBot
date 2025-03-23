from models.cars import AuctionCar
from parsers.base_parser import BasicParser
from config import COPART_URL


class CopartParser(BasicParser):
    def __init__(self, copart_url: str):
        super().__init__()
        self.url = copart_url

    async def get_data(self):
        await self.get_session()
        car_code = self.url.split("/")[4]
        copart_url = f"{COPART_URL}{car_code}"
        car_data = await self.get_copart_json(copart_url=copart_url, referer=self.url)
        if not car_data:
            return False
        brand = car_data["data"]["lotDetails"]["mkn"]
        model = car_data["data"]["lotDetails"]["lmg"]
        year = car_data["data"]["lotDetails"]["lcy"]
        image = car_data["data"]["lotDetails"]["tims"]
        engine = float(
            car_data["data"]["lotDetails"]["egn"].split(" ")[0].replace("L", "").strip()
        )
        await self.close_session()

        if "class" in model.lower():
            model = model.lower().replace("class", "klass").replace(" ", "")
        if "series" in model.lower():
            model = model.lower().replace("series", "seriya").replace(" ", "-")

        return AuctionCar(
            brand=brand,
            model=model,
            year=year,
            engine=engine,
            url=self.url,
            image=image,
        )
