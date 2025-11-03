from aiogram import Router, F
from aiogram.types import Message


router = Router(name="tracking-stop-router")


@router.message(F.text == "💥 Остановить.")
async def add_car(message: Message):
    await message.answer(
        "Трекинг остановлен.",
    )
