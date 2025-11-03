from fake_useragent import UserAgent

from src.app.logger import get_logger
from src.app.settings import get_settings
from src.parsers.heders.CopartHeaders import (
    COPART_IMAGE_HEADERS,
)
from src.parsers.models.CarModel import AuctionCar
from src.service.parser_service.AioHttpService import aiohttp_service
from src.service.parser_service.PlayWrightService import playwright

logger = get_logger()
settings = get_settings()


class CopartParser:
    def __init__(self):
        self.http_service = aiohttp_service
        self.ua = UserAgent()
        self._copart_lot_image_url = settings.COPART_LOT_IMAGES_URL
        self._copart_main_url = settings.COPART_MAIN_URL
        self._copart_lot_url = settings.COPART_LOT_URL

    async def fetch_car_data(self, url: str, car_id: str):

        referer = f"{self._copart_main_url}lot/{car_id}"

        # get image
        images_data = await self.get_copart_lot_images(
            car_id=car_id, referer=referer
        )
        # get json
        car_data = await self.get_copart_json(car_id=car_id)
        await self.http_service.close_session()

        if not car_data:
            return False

        lot_details = car_data.get("data", {}).get("lotDetails", {})

        # image list
        images = None
        if images_data:
            images = [
                img.get("highResUrl")
                for img in images_data.get("data", {})
                .get("imagesList", {})
                .get("IMAGE", [])
            ] or None
        engine_type = lot_details.get("ft")
        brand = lot_details.get("mkn")
        model = lot_details.get("lmg", "")
        year = lot_details.get("lcy")
        image = (
            lot_details.get("tims", "")
            .replace("lpp", "ids-c-prod-lpp")
            .replace("_thb", "_hrs")
        )

        engine_str = (
            lot_details.get("egn", "0").split(" ")[0].replace("L", "").strip()
        )
        try:
            engine = float(engine_str)
        except ValueError:
            engine = None

        dynamic = lot_details.get("dynamicLotDetails", {})
        buy_now = dynamic.get("buyTodayBid")
        current_bid = dynamic.get("currentBid")
        sales_status = dynamic.get("saleStatus")
        main_damage = lot_details.get("dd")
        secondary_damage = lot_details.get("sdd")

        model = await self.normalize_model_name(model=model, lot_data=car_data)

        return AuctionCar(
            brand=brand,
            model=model,
            year=year,
            engine_capacity=engine,
            engine_type=engine_type,
            url=referer,
            image=image,
            buy_now=buy_now,
            current_bid=current_bid,
            sales_status=sales_status,
            main_damage=main_damage,
            secondary_damage=secondary_damage,
            images=images,
        )

    @staticmethod
    async def normalize_model_name(model: str, lot_data: dict) -> str:
        """Get valid model"""

        model_lower = model.lower()

        # будет расти тк я еще не все марки/модели прошел ;(
        replacements = {
            "class": lambda m: m.replace("class", "klass").replace(" ", ""),
            "series": lambda m: m.replace("series", "seriya").replace(" ", "-"),
            "glc": lambda m: m.replace("-klass", ""),
            "clc": lambda m: "clc",
            "gle": lambda m: "gle",
            "glb": lambda m: "glb",
            "taos": lambda m: "taos",
            "crv": lambda m: m.replace("crv", "cr-v"),
            "s60": lambda m: "s60",
            "xc60": lambda m: "xc60",
        }

        lot_model_name = (
            lot_data.get("data", {}).get("lotDetails", {}).get("lm", "").lower()
        )
        if "rs" in model_lower and "q8" in lot_model_name:
            return "rs-q8"

        for key, func in replacements.items():
            if key in model_lower:
                return func(model_lower)

        return model_lower

    async def get_cookies_for_image(self):
        COPART_IMAGE_HEADERS["User-Agent"] = self.ua.random
        params = {
            "headers": COPART_IMAGE_HEADERS,
        }
        return await self.http_service.get_cookies(
            url=self._copart_main_url, **params
        )

    async def get_copart_lot_images(self, car_id, referer: str) -> dict:
        COPART_IMAGE_HEADERS["User-Agent"] = self.ua.random
        COPART_IMAGE_HEADERS["referer"] = referer
        params = {
            "headers": COPART_IMAGE_HEADERS,
        }
        json_data = {
            "lotNumber": car_id,
        }
        cookies = await self.get_cookies_for_image()
        return await self.http_service.post_data(
            url=self._copart_lot_image_url,
            **params,
            cookies=cookies,
            json_data=json_data,
        )

    async def get_copart_json(self, car_id: str) -> dict:
        url = f"{self._copart_lot_url}{car_id}"
        return await playwright.get_data_for_copart(url)

        # подумай почему не работает !!!!
        # COPART_CAR_HEADER["User-Agent"] = self.ua.random
        #
        # params = {
        #     "headers": COPART_CAR_HEADER,
        # }
        # return await self.http_service.get_json_data(url=url, **params)


copart_parser = CopartParser()
