from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="main-menu-router")


@router.message(Command("start"))
async def handle_start_command(
    message: Message,
):
    await message.answer(text="Test")
