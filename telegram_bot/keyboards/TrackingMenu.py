import json
import os
from datetime import datetime

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def load_cars():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(project_root, "cars_structured.json")
    with open(file_path, "r", encoding="utf-8") as file:
        cars = json.load(file)
        return cars

cars = load_cars()

async def tracking_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🚗 Запустить"),
                KeyboardButton(text="🛑 Остановить отслеживание"),
                KeyboardButton(text="📋 Список отслеживания"),
            ],
            [
                KeyboardButton(text="➕ Добавить авто"),
                KeyboardButton(text="❌ Удалить авто"),
            ],
            [
                KeyboardButton(text="💳 Изменить тариф (Отслеживание)"),
                KeyboardButton(text="⬅️ Назад в меню"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие 🚗",
    )



async def create_brands_keyboard_bidcars():
    buttons = []
    brands = set()
    for car in cars:
        if car and car not in brands:
            brands.add(car)
            buttons.append(
                [InlineKeyboardButton(text=car, callback_data=f"brand:{car}")]
            )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def create_models_keyboards_bidcars(brand: str):
    buttons = []

    models = cars.get(brand)
    for model in models:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=model,
                    callback_data=f"model:{model}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_years_keyboard_bidcars(data:dict):
    # todo какой пзц подумаю как улучшить
    buttons = []
    models = cars.get(data['brand'])
    generations = models.get(data['model'], {}).get("generations", [])


    # if generations and len(generations) == 1 and generations[0] is None:
    #     generations = None

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
        year_count = models.get("year_count", [])
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
                        text=f"{data['model']} (нет данных)",
                        callback_data="unknown_year",
                    )
                ]
            )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

