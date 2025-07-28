from datetime import datetime
import json

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


class KeyboardFactory:

    def __init__(self, brands: list[str]):
        self.brands = brands
        self.cars = self._load_cars()

    def _load_cars(self):
        with open("cars.json", "r", encoding="utf-8") as file:
            cars = json.load(file)
            return cars

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

    async def create_brands_keyboard_bidcars(self):
        buttons = []
        brands = set()

        for car in self.cars:
            make = car.get("make", "").strip()
            if make and make not in brands:
                brands.add(make)
                buttons.append(
                    [InlineKeyboardButton(text=make, callback_data=f"brand:{make}")]
                )

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def create_models_keyboards_bidcars(self, brand: str):
        buttons = []

        for car in self.cars:
            if car.get("make").lower() == brand.lower():
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=car.get("model").upper(),
                            callback_data=f"model:{car.get("model")}",
                        )
                    ]
                )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def create_years_keyboard_bidcars(self, model: str):
        # todo какой пзц подумаю как улучшить
        buttons = []
        for car in self.cars:
            if car.get("model", "").lower() == model.lower():
                generations = car.get("generations")

                if generations and len(generations) == 1 and generations[0] is None:
                    generations = None

                if generations:
                    for gen in generations:
                        if not gen:
                            continue
                        text = f"{gen.get('name', 'Неизвестно')} ({gen.get('min_year', '?')}-{gen.get('max_year', '?')})"
                        callback = (
                            f"{gen.get('min_year', '0')}:{gen.get('max_year', '0')}"
                        )
                        buttons.append(
                            [InlineKeyboardButton(text=text, callback_data=callback)]
                        )
                else:
                    year_count = car.get("year_count", [])
                    if year_count:
                        buttons.append(
                            [
                                InlineKeyboardButton(
                                    text="All generation",
                                    callback_data=f"all:1900:{datetime.now().year}",
                                )
                            ]
                        )
                    else:
                        buttons.append(
                            [
                                InlineKeyboardButton(
                                    text=f"{model.upper()} (нет данных)",
                                    callback_data="unknown_year",
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
