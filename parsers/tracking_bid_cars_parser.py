import asyncio

from config import BID_CARS_TRACKING_URL
from parsers.base_parser import BasicParser
from parsers.copart_parser import CopartParser
from parsers.iaai_parser import IaaiParser


class TrackingBidCarsParser(BasicParser):
    async def fetch_new_listings(self, brand, model, year_from, year_to) -> list:
        await self.get_data_tracking_bid_cars(
            brand=brand, model=model, year_from=year_from, year_to=year_to
        )

    async def track_cars_for_user(
        self, bot, user_id, chat_id, brand, model, year_from, year_to
    ):
        seen_ids = set()

        while True:
            listings = await self.fetch_new_listings(
                brand=brand,
                model=model,
                year_from=year_from,
                year_to=year_to,
            )

            new = [car for car in listings if car["id"] not in seen_ids]
            if new:
                seen_ids.update(car["id"] for car in new)
                text = f"🚗 Найдено новых авто:\n"
                for car in new[:5]:
                    text += f"• <b>{car['title']}</b> — {car['price']} USD\n"

                await bot.send_message(chat_id, text, parse_mode="HTML")

            await asyncio.sleep(900)
