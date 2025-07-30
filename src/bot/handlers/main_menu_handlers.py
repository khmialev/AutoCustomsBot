from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="main-menu-router")


@router.message(Command("start"))
async def handle_start_command(
    message: Message,
):
    await message.answer(
        text="📍 Главное меню\nВыберите действие:",
        reply_markup=await main_menu_keyboard(),
    )
