from aiogram import Router, F
from aiogram.types import Message

from telegram_bot.keyboards.calculate_menu import calculation_menu_keyboard
from telegram_bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="calculate-menu-router")


@router.message(F.text == "💰 Расчет авто")
async def show_calculate_menu(message: Message):
    await message.answer(
        "💰 Меню расчета авто:",
        reply_markup=await calculation_menu_keyboard(),
    )


@router.message(F.text == "⬅️ Назад в меню")
async def back_to_main(message: Message):
    await message.answer(
        "📍 Главное меню\nВыберите действие:",
        reply_markup=await main_menu_keyboard(),
    )
