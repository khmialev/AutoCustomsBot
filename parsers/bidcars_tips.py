import json

from config import BIDCARS_TIPS
from database.database_service import DataBaseService
from parsers.playwright_manager import PlayWrightManager


class BidCarsTips:
    pw = PlayWrightManager()
    url = BIDCARS_TIPS
    db = DataBaseService()

    async def get_cars(self):
        return await self.pw.get_bidcars_tips(self.url)

    async def save_to_db(self):
        data = await self.get_cars()
        await self.db.save_json(data)

    async def save_json(self):
        data = await self.get_cars()
        with open("../cars.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
