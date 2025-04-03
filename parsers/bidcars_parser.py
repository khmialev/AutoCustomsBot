import asyncio

from parsers.base_parser import BasicParser
from parsers.copart_parser import CopartParser
from parsers.iaai_parser import IaaiParser


class BidCars(BasicParser):
    def __init__(self, bid_cars_url: str):
        super().__init__()
        self.url = bid_cars_url
        self.use_proxy: bool = False

    async def get_data(self):
        car = None
        lot = self.url.split("/")[5].split("-")[0]
        if lot == "0":
            payload = self.url.split("/")[5].split("-")[1]
            # iaai
            iaai_url = await self.get_url_for_iaai(payload=payload)
            car = await IaaiParser(iaai_url=str(iaai_url)).get_data()

        if lot == "1":
            # copart
            car_id = self.url.split("/")[5].split("-")[1]
            copart_url = f"https://www.copart.com/lot/{car_id}/"
            car = await CopartParser(copart_url=copart_url).get_data()

        await self.close_session()
        return car
