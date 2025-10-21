import json
from bs4 import BeautifulSoup
from parsers.models.CarModel import AuctionCar
from parsers.services.PlayWrightService import playwright
from src.bot.settings import get_settings

settings = get_settings()


class IaaiParser:
    async def fetch_car_data(
        self,
        url,
    ):
        car_id = url.split("/")[-2].split("-")[-1]
        search_url = settings.IAAI_SEARCH_URL.format(car_id=car_id)
        html = await playwright.get_iaai_car_page(search_url, iaai=True)
        soup = BeautifulSoup(html, "html.parser")

        car_data = soup.find("script", {"id": "ProductDetailsVM"}).text
        data = json.loads(car_data)
        brand = data["inventoryView"]["attributes"]["Make"]
        model = data["inventoryView"]["attributes"]["Model"]
        year = data["inventoryView"]["attributes"]["Year"]
        engine_capacity = (
            data["inventoryView"]["attributes"]["DisplLiters"]
            .replace("L", "")
            .strip()
        )
        engine_type = data["inventoryView"]["attributes"]["FuelTypeCode"]
        buy_now = int(
            data["auctionInformation"]["prebidInformation"]["buyNowPrice"]
            .replace("$", "")
            .replace(",", "")
        )
        sales_status = ""
        main_damage = data["inventoryView"]["attributes"]["PrimaryDamageDesc"]
        odometer = data["inventoryView"]["vehicleInformation"]["$values"][9][
            "value"
        ]
        images = [
            settings.IAAI_IMAGE_URL.format(image_keys=i["k"])
            for i in data["inventoryView"]["imageDimensions"]["keys"]["$values"]
        ]
        # просто распарси тут вся инфа!

        if "SERIES" in model.lower():
            model = model.lower().replace("series", "seriya").replace(" ", "-")
        if "v60 cross country" in model.lower():
            model = "v60-cross-country"
        if "q5" in model.lower():
            model = "q5"
        if "5" in model.lower() and model.lower() != "q5":
            model = "5-seriya"
        if "3" in model.lower() and model.lower() != "glc 300":
            model = "3-seriya"
        if "glc 300" in model.lower():
            model = "glc"

        return AuctionCar(
            brand=brand,
            model=model,
            year=year,
            engine_capacity=engine_capacity,
            engine_type=engine_type,
            url=url,
            buy_now=buy_now,
            sales_status=sales_status,
            main_damage=main_damage,
            odometer=odometer,
            images=images,
        )


iaai_parser = IaaiParser()
