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

        # Считаем сразу все нужные цифры из CalculateCar
        common_total = car_calculate.common_total()
        discounted_common_total = car_calculate.discounted_common_total()
        big_total = car_calculate.big_total()
        discounted_big_total = car_calculate.discounted_big_total()

        lines = []

        # 1) Источник данных
        if web_car.url:
            lines.append(f"<b>Источник данных (URL):</b> {web_car.url}\n")

        # 2) Блок про автомобиль
        lines.append("🚗 <b>Автомобиль</b>")
        lines.append(f"• Бренд: <b>{web_car.brand.upper()}</b>")
        lines.append(f"• Модель: <b>{web_car.model.upper()}</b>")
        lines.append(f"• Год: <b>{web_car.year}</b>")
        lines.append(f"• Объем двигателя: <b>{web_car.engine}</b> см³\n")

        # 3) Данные по аукциону
        lines.append("• <b>Данные по аукциону</b>")
        if web_car.buy_now:
            lines.append(f"• Купить сейчас: <b>{web_car.buy_now}</b> $")
        lines.append(
            f"• Текущая ставка "
            f"({datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}): "
            f"<b>{web_car.current_bid}</b> $"
        )
        lines.append(f"• Статус продажи: <b>{web_car.sales_status}</b>")

        # 4) Повреждения
        # Вместо громоздкого if-else — простой сбор в список
        damage_lines = []
        if web_car.main_damage:
            damage_lines.append(f"• Основное повреждение: <b>{web_car.main_damage}</b>")
        if web_car.secondary_damage:
            damage_lines.append(
                f"• Вторичное повреждение: <b>{web_car.secondary_damage}</b>"
            )

        if damage_lines:
            # Добавим пустую строчку перед блоком повреждений
            lines.extend(damage_lines)
            lines.append("")  # пустая строка после блока

        # 5) Расходы
        lines.append("🚚 <b>Расходы</b>")
        lines.append(f"• Доставка: <b>{car_calculate.delivery} $</b>")
        lines.append(f"• Комиссия аукциона: <b>{car_calculate.auction_tax} $</b>")
        lines.append(f"• Декларанты: <b>{car_calculate.declorants} $</b>")
        lines.append(f"• Кнопка: <b>{car_calculate.auction_button} $</b>\n")

        # 6) Предполагаемая стоимость покупки (если есть)
        if estimated_price:
            lines.append(
                f"• <b>Предполагаемая стоимость покупки авто: {estimated_price} $</b>\n"
            )

        # 7) Пошлина на авто 3-5 лет (если car_tax есть)
        if car_calculate.car_tax is not None:
            # Определяем заголовок в зависимости от того, задана ли estimated_price
            header = (
                "Пошлина на авто ДО 3 лет"
                if estimated_price
                else "Пошлина на авто 3–5 лет"
            )
            lines.append(f"💵 <b>{header}</b>")
            lines.append(
                f"• Без льготы: <b>{car_calculate.car_tax * self.euro_usd:.2f} $</b>"
            )
            lines.append(
                f"• С учетом льготы: <b>{(car_calculate.car_tax * self.euro_usd) / 2:.2f} $</b>"
            )
            if common_total is not None:
                lines.append(" <b>-------------------------------------------</b>")
                lines.append(f"• Итог (без льготы): <b>{common_total} $</b>")
                lines.append(
                    f"• Итог (с льготой): <b>{discounted_common_total} $</b>\n"
                )

        # 8) Пошлина на авто старше 5 лет (big_car_tax)
        if car_calculate.big_car_tax is not None:
            # Аналогично выбираем заголовок
            header = (
                "Пошлина на авто 3–5 лет"
                if estimated_price
                else "Пошлина на авто СТАРШЕ 5 лет"
            )
            lines.append(f"💵 <b>{header}</b>")
            lines.append(
                f"• Без льготы: <b>{car_calculate.big_car_tax * self.euro_usd:.2f} $</b>"
            )
            lines.append(
                f"• С учетом льготы: <b>{(car_calculate.big_car_tax * self.euro_usd) / 2:.2f} $</b>"
            )
            if big_total is not None:
                lines.append(" <b>-------------------------------------------</b>")
                lines.append(f"• Итог (без льготы): <b>{big_total} $</b>")
                lines.append(f"• Итог (с льготой): <b>{discounted_big_total} $</b>\n")

        # 9) Предупреждение, если есть estimated_price
        if estimated_price:
            lines.append(
                "⚠️ <b>Внимание</b>\n"
                "Нужно <b>уточнить</b>, в каком месяце авто выпущено. "
                "Возможно, пока автомобиль будет в пути, оно попадёт в категорию «3–5 лет».\n"
            )

        # 10) Информация из базы (car)
        if car is None:
            lines.append(
                "❌ <b>Нет информации в базе</b> "
                f"по этой комбинации (Бренд: {web_car.brand.upper()}, "
                f"модель: {web_car.model}, год выпуска: {web_car.year}).\n"
            )
        elif isinstance(car, list):
            # Найдено несколько вариантов
            lines.append(
                "⚠️ <b>Внимание</b>\n"
                "Найдено <b>несколько</b> вариантов в базе по этим данным.\n"
                "Возможно, у этого бренда и года есть разные поколения или модификации.\n\n"
                "Список найденных вариантов:"
            )
            for c in car:
                gen = f" ({c.generation})" if c.generation else ""
                lines.append(
                    f"  • <b>{c.brand}</b> {c.model}{gen} "
                    f"(годы: <b>{c.year_from}–{c.year_to}</b>), "
                    f"цена от <b>{c.price_min or '—'}</b> до <b>{c.price_max or '—'}</b>$\n"
                    f"    Количество машин в продаже: <b>{c.count_cars}</b>"
                )
            lines.append(
                "\nПроверьте вручную, какой из этих вариантов вам подходит. "
                "Я не могу выбрать автоматически.\n"
            )
        else:
            # Нашёлся ровно один вариант Car
            lines.append(f"• Первая цена в РБ: <b>{car.price_min} $</b>")
            lines.append(f"• Средняя цена в РБ: <b>{car.average_price} $</b>")
            lines.append(f"• Количество машин в продаже: <b>{car.count_cars}</b>\n")

        # Превращаем список строк в один текст с переводами строк.
        text = "\n".join(lines)

        return text
