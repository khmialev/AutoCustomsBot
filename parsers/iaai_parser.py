from config import IAAI_URL, IMAGE_URL
from models.cars import AuctionCar
from parsers.base_parser import BasicParser


class IaaiParser(BasicParser):
    def __init__(self, iaai_url: str):
        super().__init__()
        self.url = iaai_url
        self.use_proxy: bool = False
        self.image_url = IMAGE_URL

    async def get_data(self):
        await self.get_session()
        car_code = self.url.split("/")[-1].split("~")[0]
        iaai_url = f"{IAAI_URL}{car_code}"
        car_data = await self.get_iaai_json(iaai_url=iaai_url, proxy=self.use_proxy)
        if not car_data:
            return False
        brand = car_data["MakeName"]
        model = car_data["ModelName"]
        year = car_data["ModelYear"]
        salvage_id = car_data["SalvageId"]
        payload = f"{salvage_id}~SID"
        images_data = await self.get_iaai_images(
            image_url=self.image_url, proxy=self.use_proxy, payload=payload
        )
        if not images_data:
            return False

        images = [
            f'https://vis.iaai.com/resizer?imageKeys={image["K"]}&width=845&height=633'
            for image in images_data["keys"]
        ]

        dirty_engine = await self.get_iaai_engine(
            iaai_url=self.url, proxy=self.use_proxy
        )
        if not dirty_engine:
            return False
        engine = float(dirty_engine.split(" ")[0].lower().replace("l", ""))

        if "SERIES" in model.lower():
            model = model.lower().replace("series", "seriya").replace(" ", "-")
        if "v60 cross country" in model.lower():
            model = "v60-cross-country"
        if "q5" in model.lower():
            model = "q5"
        if "5" in model.lower() and model.lower() != "q5":
            model = "5-seriya"
        if "3" in model.lower():
            model = "3-seriya"

        await self.close_session()
        return AuctionCar(
            brand=brand,
            model=model,
            year=year,
            engine=engine,
            url=self.url,
            images=images,
        )
