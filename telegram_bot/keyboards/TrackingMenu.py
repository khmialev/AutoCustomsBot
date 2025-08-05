from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def tracking_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Список отслеживания")],
            [KeyboardButton(text="➕ Добавить авто")],
            [KeyboardButton(text="❌ Удалить авто")],
            [KeyboardButton(text="💳 Изменить тариф (Отслеживание)")],
            [KeyboardButton(text="⬅️ Назад в меню")],
        ],
        resize_keyboard=True,
    )
