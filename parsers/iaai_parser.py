from config import IAAI_URL
from models.cars import AuctionCar
from parsers.base_parser import BasicParser


class IaaiParser(BasicParser):
    def __init__(self, iaai_url: str):
        super().__init__()
        self.url = iaai_url
        self.use_proxy: bool = False

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
        branch_number = car_data["AdministrativeBranchNumber"]
        image_url = f"https://vis.iaai.com/resizer?imageKeys={salvage_id}~SID~B{branch_number}~S0~I1~RW2576~TH0&width=845&height=633"
        images = [
            f"https://vis.iaai.com/resizer?imageKeys={salvage_id}~SID~B{branch_number}~S0~I{i}~RW2576~TH0&width=845&height=633"
            for i in range(1, 10)
        ]

        dirty_engine = await self.get_iaai_engine(
            iaai_url=self.url, proxy=self.use_proxy
        )
        if not dirty_engine:
            return False
        engine = float(dirty_engine.split(" ")[0].lower().replace("l", ""))

        if "SERIES" in brand.lower():
            model = model.lower().replace("series", "seriya").replace(" ", "-")

        await self.close_session()
        return AuctionCar(
            brand=brand,
            model=model,
            year=year,
            engine=engine,
            url=self.url,
            image=image_url,
            images=images,
        )
