from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🚗 Отслеживание авто"),
                KeyboardButton(text="💰 Расчет авто"),
            ],
            [
                KeyboardButton(text="📦 Мои подписки"),
                KeyboardButton(text="ℹ️ Помощь"),
            ],
            [],
        ],
        resize_keyboard=True,
    )
