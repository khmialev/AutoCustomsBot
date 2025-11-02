import json
from datetime import datetime

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def load_cars():
    with open("./cars_structured.json", "r", encoding="utf-8") as file:
        cars = json.load(file)
        return cars


cars = load_cars()


async def tracking_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🚗 Запустить"),
                KeyboardButton(text="💥 Остановить."),
            ],
            [
                KeyboardButton(text="➕ Добавить авто"),
                KeyboardButton(text="❌ Удалить авто"),
            ],
            [
                KeyboardButton(text="📋 Список отслеживания"),
                KeyboardButton(text="💳 Изменить тариф (Отслеживание)"),
            ],
            [KeyboardButton(text="⬅️ Назад в меню")],
        ],
        resize_keyboard=True,
    )


async def create_brands_keyboard_bidcars():
    buttons = []

    for car in cars:
        buttons.append(
            [InlineKeyboardButton(text=car, callback_data=f"brand:{car}")]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_models_keyboards_bidcars(brand: str):
    buttons = []

    brands = cars.get(brand, [])
    for model in brands.keys():
        buttons.append(
            [
                InlineKeyboardButton(
                    text=model,
                    callback_data=f"model:{model}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_years_keyboard_bidcars(brand: str, model: str):
    # todo какой пзц подумаю как улучшить
    buttons = []
    generations = cars.get(brand, []).get(model, [])
    if generations and len(generations) == 1 and generations[0] is None:
        generations = None
    if generations:
        for gen in generations:
            name = gen.get("name", "Неизвестно")
            years = gen.get("years", "Неизвестно")
            if years != "Неизвестно":
                year_from, year_to = years.split(
                    "–"
                )  # тут не "-", а длинное тире
            else:
                year_from, year_to = "?", "?"
            text = f"{name} ({year_from} - {year_to})"
            callback = f"{year_from} - {year_to}"
            buttons.append(
                [InlineKeyboardButton(text=text, callback_data=callback)]
            )
    else:
        year_count = generations.get("year_count", [])
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
