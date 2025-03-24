from aiogram import Bot, Dispatcher
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

import Logger
from Logger import MyLogger
from config import TOKEN, EURO_USD, brands
from database.database_service import DataBaseService
from database.db_models import Car
from models.cars import CalculateCar, AuctionCar


class BaseBot:
    def __init__(self):
        # Инициализируем Bot и Dispatcher
        self.bot = Bot(token=TOKEN)
        self.dp = Dispatcher()
        self.logger: Logger = MyLogger()
        self.euro_usd: float = float(EURO_USD)
        self.db: DataBaseService = DataBaseService()
        self.car_brands = brands
        self.car_models: list[Car] = []

    async def _create_models_keyboards(self):
        """Кнопки для выбора модели авто"""

        buttons = []
        for model in self.car_models:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{model.upper()}",
                        callback_data=f"model:{model}",
                    )
                ]
            )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def _create_brands_keyboard(self, spec=False):
        """Кнопки для выбора бренда авто"""

        buttons = []
        for brand in self.car_brands:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=brand.upper(),
                        callback_data=brand if not spec else f"spec_{brand}",
                    )
                ]
            )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def _calculation_for_data(self):
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

    async def _stop_keyboard(self):
        """Создаём кнопку для остановки обновления в бд"""

        button = [
            [
                InlineKeyboardButton(
                    text="⏹️ Остановить обновление", callback_data="stop_update"
                )
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=button)

    async def _create_main_keyboard_for_udate_db(self):
        """Создаём меню для обновления бд"""
        buttons = [
            [InlineKeyboardButton(text="Все бренды авто", callback_data="all_brands")],
            [InlineKeyboardButton(text="Конкретный бренд", callback_data="brand")],
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def _create_main_keyboard(self):
        """Главное меню"""
        buttons = [
            ["Расчет по ссылке с copart", "Расчет по ссылке с iaai"],
            ["Обновить БД с ценами (av.by)", "Расчет по данным"],
        ]

        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[KeyboardButton(text=btn) for btn in row] for row in buttons],
        )

        return keyboard

    async def get_text(
        self,
        web_car: AuctionCar,
        car_calculate: CalculateCar,
        estimated_price: float = None,
    ):

        car: list[Car] | Car = await self.db.get_car_price(
            brand=web_car.brand,
            model=web_car.model,
            year=web_car.year,
        )

        common_total = car_calculate.common_total()
        discounted_common_total = car_calculate.discounted_common_total()
        big_total = car_calculate.big_total()
        discounted_big_total = car_calculate.discounted_big_total()

        # Собираем сообщение
        text = f"🚗 <b>Автомобиль</b>\n"

        if web_car.url:
            text += f"• Источник данных (URL): <b>{web_car.url}</b>\n"

        text += (
            f"• Бренд: <b>{web_car.brand.upper()}</b>\n"
            f"• Модель: <b>{web_car.model.upper()}</b>\n"
            f"• Год: <b>{web_car.year}</b>\n\n"
            f"🔧 <b>Характеристики</b>\n"
            f"• Объем двигателя: <b>{web_car.engine}</b> см³\n\n"
        )

        text += (
            f"🚚 <b>Дополнительные расходы</b>\n"
            f"• Доставка: <b>{car_calculate.delivery} $</b>\n"
            f"• Комиссия аукциона: <b>{car_calculate.auction_tax} $</b>\n"
            f"• Декларанты: <b>{car_calculate.declorants} $</b>\n"
            f"• Кнопка: <b>{car_calculate.auction_button} $</b>\n\n"
        )

        if estimated_price:
            text += f"• <b>Предполагаемая стоимость покупки авто: {estimated_price} $</b>\n\n"

        # Добавим информацию об обычной пошлине, если она есть
        if car_calculate.car_tax is not None:
            text += (
                f"💵 <b>{'Пошлина на авто 3-5 лет' if not estimated_price else 'Пошлина на авто ДО 3 лет'}</b>\n"
                f"• Без льготы: <b>{car_calculate.car_tax * self.euro_usd} $</b>\n"
                f"• С учетом льготы: <b>{(car_calculate.car_tax * self.euro_usd) / 2} $</b>\n"
            )
            if common_total is not None:
                text += (
                    f"• Итог (без льготы): <b>{common_total} $</b>\n"
                    f"• Итог (с льготой): <b>{discounted_common_total} $</b>\n\n"
                )

        # Добавим информацию о большой пошлине, если она есть
        if car_calculate.big_car_tax is not None:
            text += (
                f"💵 <b>{'Пошлина на авто СТАРШЕ 5 лет' if not estimated_price else 'Пошлина на авто 3-5 лет'}</b>\n"
                f"• Без льготы: <b>{round(car_calculate.big_car_tax * self.euro_usd, 2)} $</b>\n"
                f"• С учетом льготы: <b>{round((car_calculate.big_car_tax * self.euro_usd) / 2)} $</b>\n"
            )
            if big_total is not None:
                text += (
                    f"• Итог (без льготы): <b>{big_total} $</b>\n"
                    f"• Итог (с льготой): <b>{discounted_big_total} $</b>\n\n"
                )

        if estimated_price:
            text += (
                "⚠️ <b>Внимание</b>\n"
                "Нужно <b>уточнить</b>, в каком месяце авто выпущено. "
                "Возможно, пока автомобиль будет в пути, он попадёт в категорию «3–5 лет».\n\n"
            )

        if car is None:
            # Вообще ничего не нашли
            text += (
                "❌ <b>Нет информации в базе</b> "
                f"по этой комбинации (Бренд: {web_car.brand.upper()}, модель: {web_car.model}, год выпуска: {web_car.year}).\n\n"
            )
        elif isinstance(car, list):
            # Найдено несколько вариантов
            text += (
                "⚠️ <b>Внимание</b>\n"
                "Найдено <b>несколько</b> вариантов в базе по этим данным.\n"
                "Возможно, у этого бренда и года есть разные поколения или модификации.\n\n"
                "Список найденных вариантов:\n"
            )
            for c in car:
                gen = f" ({c.generation})" if c.generation else ""
                text += (
                    f"  • <b>{c.brand}</b> {c.model}{gen} "
                    f"(годы: <b>{c.year_from}–{c.year_to}</b>), "
                    f"цена от <b>{c.price_min or '—'}</b> до <b>{c.price_max or '—'}</b>$\n"
                    f"Количество машин в продаже: <b>{c.count_cars}</b>\n"
                )
            text += (
                "\nПроверьте вручную, какой из этих вариантов вам подходит. "
                "Я не могу выбрать автоматически.\n\n"
            )
        else:
            # Это ровно один объект Car (ваш текущий код)
            # Выводим информацию о car (price_min, average_price, etc.)
            text += (
                f"• Первая цена в РБ: <b>{car.price_min} $</b>\n"
                f"• Средняя цена в РБ: <b>{car.average_price} $</b>\n\n"
                f"• Количество машин в продаже: <b>{car.count_cars} </b>\n\n"
            )

        return text
