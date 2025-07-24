from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from calculation.car_calculator import CalculateLogic
from models.cars import CalculateCar
from telegram_bot.states.fsm_states import ManualBasicCalcStates


class ManualBasicCalculator:
    def __init__(self, bot):
        self.bot = bot

        # -----------------------------
        #   Логика базового расчёта (CarCalcStates)
        # -----------------------------
        self.bot.dp.callback_query.register(
            self.base_calculate, F.data == "base_calculation"
        )
        # Хендлер, где пользователь вводит объём (waiting_for_engine)
        self.bot.dp.message.register(
            self.process_engine_input,
            ManualBasicCalcStates.waiting_for_engine,
        )
        # Хендлер, где пользователь вводит год (waiting_for_year)
        self.bot.dp.message.register(
            self.process_year_input, ManualBasicCalcStates.waiting_for_year
        )
        # Хендлер, где пользователь вводит бренд (waiting_for_brand)
        self.bot.dp.message.register(
            self.process_brand_input, ManualBasicCalcStates.waiting_for_brand
        )

    async def base_calculate(self, call: CallbackQuery, state: FSMContext):
        """Базовый расчет"""
        await call.message.answer(
            text="🔢 <b>Введите объём двигателя</b> в литрах "
            "(например, можно ввести <code>2.0</code>, <code>20</code> или <code>2000</code> — все варианты означают 2.0 литра):",
            parse_mode="HTML",
        )
        await state.set_state(ManualBasicCalcStates.waiting_for_engine)
        await call.answer()  # Закрываем "часики" на кнопке

    async def process_engine_input(self, message: Message, state: FSMContext):
        engine_value = float(message.text.strip())

        # Сохраняем в FSM данные (в контексте)
        await state.update_data({"engine": engine_value})

        # Переходим к следующему состоянию (ждем год авто)
        await state.set_state(ManualBasicCalcStates.waiting_for_year)

        # Спрашиваем год
        await message.answer(
            "📅 <b>Введите год выпуска</b> (например, <code>2015</code>):",
            parse_mode="HTML",
        )

    async def process_year_input(self, message: Message, state: FSMContext):
        year_text = message.text.strip()

        if not year_text.isdigit():
            await message.answer(
                "❌ Пожалуйста, введите целое число (например, 2015). Попробуйте ещё раз."
            )
            return

        year_value = int(year_text)

        # Получаем сохранённый ранее объём двигателя
        data = await state.get_data()
        engine_value = data.get("engine")

        car_calculate: CalculateCar = await CalculateLogic().calculate(
            car_manufacture_year=year_value, engine_volume=engine_value
        )

        common_total = car_calculate.common_total()
        discounted_common_total = car_calculate.discounted_common_total()
        big_total = car_calculate.big_total()
        discounted_big_total = car_calculate.discounted_big_total()

        text = (
            f"🚚 <b>Дополнительные расходы</b>\n"
            f"• Доставка: <b>{car_calculate.delivery} $</b>\n"
            f"• Комиссия аукциона: <b>{car_calculate.auction_tax} $</b>\n"
            f"• Декларанты: <b>{car_calculate.declorants} $</b>\n"
            f"• Кнопка: <b>{car_calculate.auction_button} $</b>\n\n"
        )

        # Добавим информацию об обычной пошлине, если она есть
        if car_calculate.car_tax is not None:
            text += (
                f"💰 <b>Обычная пошлина</b>\n"
                f"• Без льготы: <b>{car_calculate.car_tax * self.bot.euro_usd} $</b>\n"
                f"• С учетом льготы: <b>{(car_calculate.car_tax * self.bot.euro_usd) / 2} $</b>\n"
            )
            if common_total is not None:
                text += (
                    f"• Итог (без льготы): <b>{common_total} $</b>\n"
                    f"• Итог (с льготой): <b>{discounted_common_total} $</b>\n\n"
                )

        # Добавим информацию о большой пошлине, если она есть
        if car_calculate.big_car_tax is not None:
            text += (
                f"💰 <b>Большая пошлина</b>\n"
                f"• Без льготы: <b>{car_calculate.big_car_tax * self.bot.euro_usd} $</b>\n"
                f"• С учетом льготы: <b>{(car_calculate.big_car_tax * self.bot.euro_usd) / 2} $</b>\n"
            )
            if big_total is not None:
                text += (
                    f"• Итог (без льготы): <b>{big_total} $</b>\n"
                    f"• Итог (с льготой): <b>{discounted_big_total} $</b>\n\n"
                )
        await message.answer(text, parse_mode="HTML")
        await state.clear()

    async def process_brand_input(self, message: Message, state: FSMContext):
        """
        Когда пользователь вводит текст, находясь в состоянии waiting_for_brand.
        """
        brand = message.text
        await message.answer(
            f"✅ <b>Бренд принят:</b> <code>{brand}</code>\n"
            "Начинаю обновление цен...",
            parse_mode="HTML",
        )
        try:
            await self.bot.av_parser.run_parser(brand)
            await message.answer(
                f"✅ <b>Успешно обновили цены</b> для бренда: <b>{brand}</b>!",
                parse_mode="HTML",
            )
        except:
            await message.answer(
                f"❌ <b>Ошибка при обновлении</b> для бренда: <b>{brand}</b>.",
                parse_mode="HTML",
            )
        await state.clear()
