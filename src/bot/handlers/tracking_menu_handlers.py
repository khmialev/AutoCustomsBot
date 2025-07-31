from aiogram import Router, F
from aiogram.types import Message

from src.bot.handlers.constants.emojs import CAR, LOCATION
from src.bot.handlers.constants.texts import (
    SHOW_TRACKING_MENU,
    HANDLE_START_COMMAND,
)
from telegram_bot.keyboards.main_menu import main_menu_keyboard
from telegram_bot.keyboards.tracking_menu import tracking_menu_keyboard

router = Router(name="tracking-menu-router")


@router.message(F.text == "🚗 Отслеживание авто")
async def show_tracking_menu(message: Message):
    await message.answer(
        text=f"{CAR} {SHOW_TRACKING_MENU}",
        reply_markup=await tracking_menu_keyboard(),
    )


@router.message(F.text == "⬅️ Назад в меню")
async def back_to_main(message: Message):
    await message.answer(
        text=f"{LOCATION} {HANDLE_START_COMMAND}",
        reply_markup=await main_menu_keyboard(),
    )
