from aiogram import Bot, Dispatcher


import Logger
from Logger import MyLogger
from config import TOKEN, EURO_USD, brands
from database.database_service import DataBaseService
from telegram_bot.keyboards.keyboards_factory import KeyboardFactory
from telegram_bot.texts.texts import CarTextGenerator


class BaseBot:
    def __init__(self):
        # Инициализируем Bot и Dispatcher
        self.bot = Bot(token=TOKEN)
        self.dp = Dispatcher(bot=self.bot)
        self.logger: Logger = MyLogger()
        self.euro_usd: float = float(EURO_USD)
        self.db: DataBaseService = DataBaseService()
        self.car_brands = brands

        self.keyboards: KeyboardFactory = KeyboardFactory(self.car_brands)
        self.texts: CarTextGenerator = CarTextGenerator(self.euro_usd, self.db)

    async def main(self):
        """
        Основной метод, запускающий бесконечный polling.
        """
        await self.dp.start_polling(self.bot)
