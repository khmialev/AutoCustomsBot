from aiogram.exceptions import TelegramBadRequest
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
from telegram_bot.bid_cars import BidCarsUrlCalculator
from telegram_bot.copart_url_calculator import CopartUrlCalculator
from telegram_bot.iaai_url_calculator import IaaiUrlCalculator
from telegram_bot.manual_basic_calculator import ManualBasicCalculator
from telegram_bot.manual_spec_calculator import ManualSpecCalculator
from telegram_bot.tracking_bidcars import BidCarsTracking
from telegram_bot.update_db_handler import UpdateDBHandler


class CarBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.av_parser: AVParser = AVParser()

        self.tracking_bidcars = BidCarsTracking(self)
        self.bid_cars = BidCarsUrlCalculator(self)
        self.update_db_handler = UpdateDBHandler(self)

        self.copart_url_calculator = CopartUrlCalculator(self)
        self.iaai = IaaiUrlCalculator(self)

        self.manual_basic_calculator = ManualBasicCalculator(self)
        self.manual_spec_calculator = ManualSpecCalculator(self)

        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.calculate_for_data, F.text == "Расчет по данным")



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
            reply_markup=await self.keyboards.create_main_keyboard(),
            parse_mode="HTML",
        )

    async def calculate_for_data(self, message: Message):
        """Кнопка расчет оп данным"""
        await message.answer(
            text="Хорошо! Теперь выбери действие для расчета платежей за автомобиль:",
            reply_markup=await self.keyboards.calculation_for_data(),
            parse_mode="HTML",
        )
        # удалить клаву

    async def process_car_price_for_under_3_years(
        self, message: Message, state: FSMContext
    ):
        estimated_price = message.text.strip()
        try:
            car_price = float(estimated_price)
        except ValueError:
            await message.answer("❌ Пожалуйста, введите число (например, 15000).")
            return

        data = await state.get_data()
        car = data.get("car")
        if not car:
            await message.answer("Данные о машине не найдены, начните заново.")
            await state.clear()
            return

        await self.process_final_car_data(
            message=message,
            auction_car=car,
            state=state,
            estimated_price=car_price,
        )

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

        text = await self.texts.get_text(
            web_car=auction_car,
            car_calculate=car_calculate,
            estimated_price=estimated_price,
        )

        if auction_car.images:
            try:
                media = [
                    InputMediaPhoto(
                        media=auction_car.images[0], caption=text, parse_mode="HTML"
                    )
                ] + [InputMediaPhoto(media=url) for url in auction_car.images[1:10]]
                await message.answer_media_group(media)
            except TelegramBadRequest:
                text = await self.texts.get_text(
                    web_car=auction_car,
                    car_calculate=car_calculate,
                    estimated_price=estimated_price,
                    msg_to_long=True,
                )
                await message.answer_photo(
                    photo=auction_car.image,
                    caption=text,
                    parse_mode="HTML",
                )
            except:
                await message.answer_photo(
                    photo=auction_car.image, caption=text, parse_mode="HTML"
                )

        elif auction_car.image:
            await message.answer_photo(
                photo=auction_car.image, caption=text, parse_mode="HTML"
            )
        else:
            await message.answer(text, parse_mode="HTML")
        await state.clear()
