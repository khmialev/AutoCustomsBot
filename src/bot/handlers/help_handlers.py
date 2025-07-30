from aiogram import Router, F
from aiogram.types import Message

from telegram_bot.texts.help_text import tariffs_html

router = Router(name="help-router")


@router.message(F.text == "ℹ️ Помощь")
async def handle_help_command(
    message: Message,
):
    await message.answer(
        text=tariffs_html,
        parse_mode="HTML",
    )
