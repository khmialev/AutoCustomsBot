from aiogram import Router, F
from aiogram.types import Message


router = Router(name="tracking-start-router")


@router.message(F.text == "🚗 Запустить")
async def add_car(message: Message):
    await message.answer(
        "Трекинг запущен.",
    )
