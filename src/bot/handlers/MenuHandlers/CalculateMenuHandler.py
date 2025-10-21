from aiogram import Router, F
from aiogram.types import Message

from src.bot.constants.emojis import MONEY_BAG, LOCATION
from src.bot.constants.texts import (
    SHOW_CALCULATE_MENU,
    HANDLE_START_COMMAND,
)
from telegram_bot.keyboards.CalculateMenu import calculation_menu_keyboard
from telegram_bot.keyboards.MainMenu import main_menu_keyboard

router = Router(name="calculate-menu-router")


@router.message(F.text == "💰 Расчет авто")
async def show_calculate_menu(message: Message):
    await message.answer(
        text=f"{MONEY_BAG} {SHOW_CALCULATE_MENU}",
        reply_markup=await calculation_menu_keyboard(),
    )


@router.message(F.text == "⬅️ Назад в меню")
async def back_to_main(message: Message):
    await message.answer(
        text=f"{LOCATION} {HANDLE_START_COMMAND}",
        reply_markup=await main_menu_keyboard(),
    )
