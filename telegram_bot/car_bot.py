from aiogram.filters import Command
from aiogram.types import (
    Message,
)
from aiogram import F

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
            reply_markup=await self._create_reply_keyboard(),
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
