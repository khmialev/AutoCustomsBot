from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.handlers.constants.emojs import LOCATION
from src.bot.handlers.constants.texts import HANDLE_START_COMMAND
from telegram_bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="main-menu-router")


@router.message(Command("start"))
async def handle_start_command(
    message: Message,
):
    await message.answer(
        text=f"{LOCATION} {HANDLE_START_COMMAND}",
        reply_markup=await main_menu_keyboard(),
    )
