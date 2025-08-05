from aiogram import Router, F
from aiogram.types import Message


router = Router(name="tracking-add-router")


@router.message(F.text == "➕ Добавить авто")
async def add_car(message: Message):
    await message.answer(
        "Введите данные автомобиля для добавления...",
    )
