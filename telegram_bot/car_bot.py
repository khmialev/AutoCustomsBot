from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
)
from aiogram import F
from aiogram.types import InputMediaPhoto

from calculation.car_calculator import CalculateLogic
from models.cars import CalculateCar, AuctionCar
from parsers.av_parser import AVParser
from telegram_bot.base_bot import BaseBot
from telegram_bot.copart_url_calculator import CopartUrlCalculator
from telegram_bot.iaai_url_calculator import IaaiUrlCalculator
from telegram_bot.manual_basic_calculator import ManualBasicCalculator
from telegram_bot.manual_spec_calculator import ManualSpecCalculator
from telegram_bot.update_db_handler import UpdateDBHandler


class CarBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.av_parser: AVParser = AVParser()

        self.update_db_handler = UpdateDBHandler(self)
        self.copart_url_calculator = CopartUrlCalculator(self)
        self.iaai = IaaiUrlCalculator(self)
        self.manual_basic_calculator = ManualBasicCalculator(self)
        self.manual_spec_calculator = ManualSpecCalculator(self)

        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.calculate_for_data, F.text == "Расчет по данным")

    async def main(self):
        """
        Основной метод, запускающий бесконечный polling.
        """
        await self.dp.start_polling(self.bot)

    async def cmd_start(self, message: Message):
        """
        Обработчик команды /start.
        Проверяет username и, если он в ALLOWED_USERID, показывает инлайн-кнопки.
        """
        await message.answer(
            text=(
                f"Привет, <b>{message.from_user.username}</b>! ✌️\n\n"
                f"Выбери команду из меню ниже или введи её вручную:"
            ),
            reply_markup=await self._create_main_keyboard(),
            parse_mode="HTML",
        )

    async def calculate_for_data(self, message: Message):
        """Кнопка расчет оп данным"""
        await message.answer(
            text="Хорошо! Теперь выбери действие для расчета платежей за автомобиль:",
            reply_markup=await self._calculation_for_data(),
            parse_mode="HTML",
        )
        # удалить клаву

    async def process_final_car_data(
        self,
        message: Message,
        auction_car: AuctionCar,
        state: FSMContext,
        estimated_price: float = None,
    ):
        """
        Общая логика для:
         - расчёта таможенной пошлины
         - формирования текста ответа
         - отправки фото/сообщения в чат

        Параметры:
          auction_car  – объект AuctionCar, полученный от парсера
          car_price   – цена (если машина младше 3 лет); может быть None, если машина 3+ года
        """

        car_calculate: CalculateCar = await CalculateLogic().calculate(
            car_manufacture_year=auction_car.year,
            engine_volume=auction_car.engine,
            car_price=estimated_price,
        )

        text = await self.get_text(
            web_car=auction_car,
            car_calculate=car_calculate,
            estimated_price=estimated_price,
        )

        if auction_car.images:
            media = []

            media.append(
                InputMediaPhoto(
                    media=auction_car.images[0], caption=text, parse_mode="HTML"
                )
            )
            for url in auction_car.images[1:]:
                media.append(InputMediaPhoto(media=url))
            await message.answer_media_group(media)

        elif auction_car.image:
            await message.answer_photo(
                photo=auction_car.image, caption=text, parse_mode="HTML"
            )
        else:
            await message.answer(text, parse_mode="HTML")
        await state.clear()
