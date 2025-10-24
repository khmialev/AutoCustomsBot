from aiogram import Router, F
from aiogram.types import Message

from src.bot.services.TrackingManager import tracking_manager
from telegram_bot.keyboards.MainMenu import main_menu_keyboard

router = Router(name="tracking-stop-router")


@router.message(F.text == "🛑 Остановить отслеживание")
async def stop_tracking_command(message: Message):
    user_id = message.from_user.id

    if tracking_manager._is_tracking(user_id):
        await tracking_manager.stop_tracking(user_id)
        await message.answer(
            "❌ Отслеживание остановлено.",
            reply_markup=await main_menu_keyboard()
        )
    else:
        await message.answer(
            "ℹ️ У вас нет активного отслеживания.",
            reply_markup=await main_menu_keyboard(),
        )