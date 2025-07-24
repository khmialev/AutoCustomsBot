import asyncio
import random

from aiogram import Bot

from config import BID_CARS_TRACKING_URL
from models.cars import AuctionCar
from parsers.base_parser import BasicParser
from parsers.bidcars_parser import BidCars
from parsers.copart_parser import CopartParser
from parsers.iaai_parser import IaaiParser


class TrackingBidCarsParser(BasicParser):

    async def get_car_text(self, car: AuctionCar) -> str:
        text = (
            f"<b>{car.brand} {car.model} {car.year}</b>\n"
            f"🚗 <b>Объем:</b> {car.engine or '—'} л\n"
            f"💰 <b>Ставка сейчас:</b> ${car.current_bid or '—'}\n"
            f"💵 <b>Купить сейчас:</b> ${car.buy_now or '—'}\n"
            f"📊 <b>Статус:</b> {car.sales_status or '—'}\n"
            f"💥 <b>Повреждения:</b> {car.main_damage or '—'} / {car.secondary_damage or '—'}\n"
        )
        if car.url:
            text += f'🔗 <a href="{car.url}">Открыть лот</a>'
        return text

    async def track_cars_for_user(
        self, bot: Bot, user_id, chat_id, brand, model, year_from, year_to
    ):
        seen_ids = set()

        while True:
            cars_urls = await self.get_data_tracking_bid_cars(
                brand=brand,
                model=model,
                year_from=year_from,
                year_to=year_to,
            )
            for url in cars_urls:
                print(f"get url {url}")
                bid_cars: AuctionCar = await BidCars(url).get_data()
                if not bid_cars:
                    continue
                text = await self.get_car_text(bid_cars)
                await bot.send_photo(
                    caption=text,
                    chat_id=chat_id,
                    parse_mode="HTML",
                    photo=bid_cars.images[0],
                )
                await asyncio.sleep(random.randint(1, 5))

            return

            # new = [car for car in bid_cars. if car["id"] not in seen_ids]
            # if new:
            #     seen_ids.update(car["id"] for car in new)
            #     text = f"🚗 Найдено новых авто:\n"
            #     for car in new[:5]:
            #         text += f"• <b>{car['title']}</b> — {car['price']} USD\n"
            #
            #     await bot.send_message(chat_id, text, parse_mode="HTML")
            #
            # await asyncio.sleep(900)
