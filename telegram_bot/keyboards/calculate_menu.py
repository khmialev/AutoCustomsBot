from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def calculation_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📟 Сделать расчет")],
            [KeyboardButton(text="📜 История расчетов")],
            [KeyboardButton(text="🛠 Задать свои значения для расчета")],
            [KeyboardButton(text="⬅️ Назад в меню")],
        ],
        resize_keyboard=True,
    )
