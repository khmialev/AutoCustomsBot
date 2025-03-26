from models.cars import AuctionCar
from parsers.base_parser import BasicParser
from config import COPART_URL


class CopartParser(BasicParser):
    def __init__(self, copart_url: str):
        super().__init__()
        self.url = copart_url
        self.use_proxy: bool = False

    async def get_data(self):
        await self.get_session()
        if "ru" in self.url:
            self.url = self.url.replace("ru/", "")
        car_code = self.url.split("/")[4]
        copart_url = f"{COPART_URL}{car_code}"
        images_data = await self.get_copart_lot_images(
            lot_id=car_code, referer=self.url, proxy=self.use_proxy
        )

        car_data = await self.get_copart_json(
            copart_url=copart_url, referer=self.url, proxy=self.use_proxy
        )
        if not car_data:
            return False

        if images_data:
            images = [
                image["highResUrl"]
                for image in images_data["data"]["imagesList"]["IMAGE"]
            ]
        else:
            images = None

        brand = car_data["data"]["lotDetails"]["mkn"]
        model = car_data["data"]["lotDetails"]["lmg"]
        year = car_data["data"]["lotDetails"]["lcy"]
        image = (
            car_data["data"]["lotDetails"]["tims"]
            .replace("lpp", "ids-c-prod-lpp")
            .replace("_thb", "_hrs")
        )
        engine = float(
            car_data["data"]["lotDetails"]["egn"].split(" ")[0].replace("L", "").strip()
        )

        buy_now = car_data["data"]["lotDetails"]["dynamicLotDetails"]["buyTodayBid"]
        current_bid = car_data["data"]["lotDetails"]["dynamicLotDetails"]["currentBid"]
        sales_status = car_data["data"]["lotDetails"]["dynamicLotDetails"]["saleStatus"]
        main_damage = car_data["data"]["lotDetails"]["dd"]
        try:
            secondary_damage = car_data["data"]["lotDetails"]["sdd"]
        except:
            secondary_damage = None

        await self.close_session()

        if "class" in model.lower():
            model = model.lower().replace("class", "klass").replace(" ", "")
        if "series" in model.lower():
            model = model.lower().replace("series", "seriya").replace(" ", "-")
        if "glc" in model.lower():
            model = model.lower().replace("-klass", "")
        if "clc" in model.lower():
            model = "clc"
        if "gle" in model.lower():
            model = "gle"
        if "glb" in model.lower():
            model = "glb"

        return AuctionCar(
            brand=brand,
            model=model,
            year=year,
            engine=engine,
            url=self.url,
            image=image,
            buy_now=buy_now,
            current_bid=current_bid,
            sales_status=sales_status,
            main_damage=main_damage,
            secondary_damage=secondary_damage,
            images=images,
        )
