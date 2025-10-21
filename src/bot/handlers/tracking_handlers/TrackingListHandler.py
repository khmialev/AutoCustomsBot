from aiogram import Router, F
from aiogram.types import Message


router = Router(name="tracking-list-router")


@router.message(F.text == "📋 Список отслеживания")
async def tracking_list(message: Message):
    await message.answer(
        "📋 Ваш список отслеживания пуст.",
    )
