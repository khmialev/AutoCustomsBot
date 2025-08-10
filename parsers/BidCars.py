from parsers.CopartParser import copart_parser
from parsers.IaaiParser import iaai_parser


class BidCars:
    async def get_data(self, url: str):
        car = None
        lot = url.split("/")[5].split("-")[0]
        if lot == "0":
            car = await iaai_parser.fetch_car_data(url=url)

        if lot == "1":
            # copart
            car_id = url.split("/")[5].split("-")[1]
            car = await copart_parser.fetch_car_data(url=url, car_id=car_id)

        return car


bidcars = BidCars()
