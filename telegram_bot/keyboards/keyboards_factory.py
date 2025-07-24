from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


class KeyboardFactory:

    def __init__(self, brands: list[str]):
        self.brands = brands

    async def create_years_keyboard(self, years: dict):
        buttons = []

        for data in years:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"Поколение: {data['generation'].upper()}",
                        callback_data=f"{data['year_from']}_{data['year_to']}",
                    )
                ]
            )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def create_models_keyboards(self, car_models: list):
        """Кнопки для выбора модели авто"""

        buttons = []
        for model in car_models:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{model.upper()}",
                        callback_data=f"model:{model}",
                    )
                ]
            )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def create_brands_keyboard(self, spec=False):
        """Кнопки для выбора бренда авто"""

        buttons = []
        for brand in self.brands:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=brand.upper(),
                        callback_data=brand if not spec else f"spec_{brand}",
                    )
                ]
            )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def calculation_for_data(self):
        """Меню для выбора типа расчета"""
        buttons = [
            [
                InlineKeyboardButton(
                    text="Базовый расчет", callback_data="base_calculation"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Расчет с анализом", callback_data="spec_calculation"
                )
            ],
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def stop_keyboard(self):
        """Создаём кнопку для остановки обновления в бд"""

        button = [
            [
                InlineKeyboardButton(
                    text="⏹️ Остановить обновление", callback_data="stop_update"
                )
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=button)

    async def create_main_keyboard_for_udate_db(self):
        """Создаём меню для обновления бд"""
        buttons = [
            [InlineKeyboardButton(text="Все бренды авто", callback_data="all_brands")],
            [InlineKeyboardButton(text="Конкретный бренд", callback_data="brand")],
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def create_main_keyboard(self, is_tracking: bool = False):
        """Главное меню"""
        buttons = [
            [
                # "Расчет по ссылке с copart",
                # "Расчет по ссылке с iaai",
                "Расчет по ссылке с BidCars",
            ],
            ["Обновить БД с ценами (av.by)"],  # [ "Расчет по данным"],
            ["Отслеживать авто с BidCars"],
        ]
        if is_tracking:
            buttons.append(["🛑 Остановить отслеживание"])

        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[KeyboardButton(text=btn) for btn in row] for row in buttons],
        )

        return keyboard
