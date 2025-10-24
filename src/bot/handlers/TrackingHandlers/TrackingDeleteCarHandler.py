from aiogram import Router, F
from aiogram.types import Message


router = Router(name="tracking-delete-router")


@router.message(F.text == "❌ Удалить авто")
async def delete_car(message: Message):
    await message.answer(
        "Выберите авто для удаления...",
    )
