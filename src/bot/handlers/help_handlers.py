from aiogram import Router, F
from aiogram.types import Message

from src.bot.handlers.constants.static_texts import TARIFFS_HTML

router = Router(name="help-router")


@router.message(F.text == "ℹ️ Помощь")
async def handle_help_command(
    message: Message,
):
    await message.answer(
        text=TARIFFS_HTML,
        parse_mode="HTML",
    )
