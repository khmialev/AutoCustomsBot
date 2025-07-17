import datetime

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
            [
                "Расчет по ссылке с copart",
                "Расчет по ссылке с iaai",
                "Расчет по ссылке с BidCars",
            ],
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
        msg_to_long: bool = False,
    ):
        car: list[Car] | Car = await self.db.get_car_price(
            brand=web_car.brand,
            model=web_car.model,
            year=web_car.year,
        )

        # Считаем сразу все нужные цифры из CalculateCar
        common_total = car_calculate.common_total()
        discounted_common_total = car_calculate.discounted_common_total()
        big_total = car_calculate.big_total()
        discounted_big_total = car_calculate.discounted_big_total()

        lines = []

        # 1) Источник данных
        if web_car.url:
            lines.append(f"<b>Источник:</b> {web_car.url}")

        # 2) Блок про автомобиль
        lines.append("🚗 <b>Автомобиль</b>")
        lines.append(f"• Бренд: <b>{web_car.brand.upper()}</b>")
        lines.append(f"• Модель: <b>{web_car.model.upper()}</b>")
        lines.append(f"• Год: <b>{web_car.year}</b>")
        lines.append(f"• Двигатель: <b>{web_car.engine}</b> см³")

        if not msg_to_long:
            # 3) Данные по аукциону
            lines.append("🪒 <b>Данные по аукциону</b>")
            if web_car.buy_now:
                lines.append(f"• Купить сейчас: <b>{web_car.buy_now}</b> $")
            if web_car.current_bid:
                lines.append(
                    f"• Текущая ставка "
                    f"({datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}): "
                    f"<b>{web_car.current_bid}</b> $"
                )
            if web_car.sales_status:
                lines.append(f"• Статус продажи: <b>{web_car.sales_status}</b>")

        # 4) Повреждения
        if not msg_to_long:
            damage_lines = []
            if web_car.main_damage:
                damage_lines.append(
                    f"• Основное повреждение: <b>{web_car.main_damage}</b>"
                )
            if web_car.secondary_damage:
                damage_lines.append(
                    f"• Вторичные повреждение: <b>{web_car.secondary_damage}</b>"
                )

            if damage_lines:
                # Добавим пустую строчку перед блоком повреждений
                lines.extend(damage_lines)

        # 5) Расходы
        lines.append("🚚 <b>Расходы</b>")
        lines.append(f"• Доставка: <b>{car_calculate.delivery} $</b>")
        lines.append(f"• Комиссия аукциона: <b>{car_calculate.auction_tax} $</b>")
        lines.append(f"• Декларанты: <b>{car_calculate.declorants} $</b>")
        lines.append(f"• Льготник: <b>{car_calculate.disabled_person} $</b>")
        lines.append(f"• Кнопка: <b>{car_calculate.auction_button} $</b>\n")

        # 6) Предполагаемая стоимость покупки (если есть)
        if estimated_price:
            lines.append(f"• <b>Ожидаемая стоимость: {estimated_price} $</b>\n")

        # 7) Пошлина на авто 3-5 лет (если car_tax есть)
        if car_calculate.car_tax is not None:
            # Определяем заголовок в зависимости от того, задана ли estimated_price
            header = "Пошлина ДО 3 лет" if estimated_price else "Пошлина (3–5 лет)"
            lines.append(f"💵 <b>{header}</b>")
            lines.append(
                f"• Без льготы: <b>{car_calculate.car_tax * self.euro_usd:.2f} $</b>"
            )
            lines.append(
                f"• С учетом льготы: <b>{(car_calculate.car_tax * self.euro_usd) / 2:.2f} $</b>"
            )
            if common_total is not None:
                lines.append("───────────")
                lines.append(f"• Итог (без льготы): <b>{common_total} $</b>")
                lines.append(
                    f"• Итог (с льготой): <b>{discounted_common_total} $</b>\n"
                )

        # 8) Пошлина на авто старше 5 лет (big_car_tax)
        if car_calculate.big_car_tax is not None:
            # Аналогично выбираем заголовок
            header = "Пошлина (3–5 лет)" if estimated_price else "Пошлина СТАРШЕ 5 лет"
            lines.append(f"💵 <b>{header}</b>")
            lines.append(
                f"• Без льготы: <b>{car_calculate.big_car_tax * self.euro_usd:.2f} $</b>"
            )
            lines.append(
                f"• С учетом льготы: <b>{(car_calculate.big_car_tax * self.euro_usd) / 2:.2f} $</b>"
            )
            if big_total is not None:
                lines.append("───────────")
                lines.append(f"• Итог (без льготы): <b>{big_total} $</b>")
                lines.append(f"• Итог (с льготой): <b>{discounted_big_total} $</b>\n")

        # 9) Предупреждение, если таможня пересекается
        if datetime.datetime.now().year - web_car.year == 2 and estimated_price:
            lines.append(
                "⚠️ <b>Возможно, пока автомобиль будет в пути, он попадёт в категорию «3–5 лет».</b>"
            )
        if datetime.datetime.now().year - web_car.year == 5:
            lines.append(
                "⚠️ <b>Возможно, пока автомобиль будет в пути, он попадёт в категорию « СТАРШЕ 5 лет».</b>"
            )

        # 10) Информация из базы (car)
        if car is None:
            lines.append(
                f"❌ <b>Бренд: {web_car.brand.upper()},модель: {web_car.model}, год выпуска: {web_car.year}).</b> "
                f" Нет в базе\n"
            )
        elif isinstance(car, list):
            # Найдено несколько вариантов
            lines.append(
                "⚠️ <b>Найдено <b>несколько</b> вариантов в базе по этим данным:</b>"
            )
            for c in car:
                gen = f" ({c.generation})" if c.generation else ""
                lines.append(
                    f"\n• <b>{c.brand.upper()} {c.model.upper()}</b> (<b>{c.year_from}–{c.year_to}</b>)\n"
                    f"• Первая цена <b>{c.price_min or '—'}$</b>\n• Средняя цена <b>{c.average_price or '—'}</b>$\n"
                    f"Количество машин в продаже: <b>{c.count_cars}</b>"
                )
        else:
            # Нашёлся ровно один вариант Car
            lines.append(f"\n• Первая цена в РБ: <b>{car.price_min} $</b>")
            lines.append(f"• Средняя цена в РБ: <b>{car.average_price} $</b>")
            lines.append(f"• Количество машин в продаже: <b>{car.count_cars}</b>")

        # Превращаем список строк в один текст с переводами строк.
        text = "\n".join(lines)

        return text
