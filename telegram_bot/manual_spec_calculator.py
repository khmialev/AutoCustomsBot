from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from calculation.car_calculator import CalculateLogic
from models.cars import CalculateCar, AuctionCar
from telegram_bot.states.fsm_states import ManualSpecCalcStates


class ManualSpecCalculator:
    def __init__(self, bot):
        self.bot = bot

        # -----------------------------
        #   Логика специального расчёта (SpecCalcStates)
        # -----------------------------

        self.bot.dp.callback_query.register(
            self.spec_calculate, F.data == "spec_calculation"
        )

        # Хендлер выбора модели (waiting_for_model)
        self.bot.dp.callback_query.register(
            self.spec_model_selection,
            F.data.startswith("model:"),
            ManualSpecCalcStates.waiting_for_model,
        )
        # Хендлер, когда callback_data.startswith("spec") (если нужно)
        self.bot.dp.callback_query.register(self.spec_brand, F.data.startswith("spec"))
        # Хендлер ввода года (waiting_for_year)
        self.bot.dp.message.register(
            self.spec_year_selection, ManualSpecCalcStates.waiting_for_year
        )
        # Хендлер ввода объёма (waiting_for_engine)
        self.bot.dp.message.register(
            self.spec_engine_input_spec, ManualSpecCalcStates.waiting_for_engine
        )

    async def spec_calculate(self, call: CallbackQuery, state: FSMContext):
        """Специальный расчет"""

        await call.message.answer(
            "✏️ <b>Выберите название бренда:</b> ",
            parse_mode="HTML",
            reply_markup=await self.bot._create_brands_keyboard(spec=True),
        )
        await state.set_state(ManualSpecCalcStates.waiting_for_engine)

    async def spec_brand(self, call: CallbackQuery, state: FSMContext):
        """Специальный расчет, получаем бренд"""

        brand = call.data.split("_")[1]
        car_models = await self.bot.db.get_models(brand=brand.lower())
        await state.update_data({"brand": brand})
        await call.message.edit_text(
            "✏️ <b>Выберите модель бренда:</b> ",
            parse_mode="HTML",
            reply_markup=await self.bot._create_models_keyboards(car_models=car_models),
        )
        await state.set_state(ManualSpecCalcStates.waiting_for_model)
        await call.answer()

    async def spec_model_selection(self, call: CallbackQuery, state: FSMContext):
        """Специальный расчет, получаем все данные по бренду"""

        model = call.data.split(":")[1]

        # Сохраняем в state
        await state.update_data({"model_name": model})

        # Просим ввести объём двигателя
        await call.message.answer(
            "📅 <b>Введите год выпуска</b> (например, <code>2015</code>):",
            parse_mode="HTML",
        )

        await state.set_state(ManualSpecCalcStates.waiting_for_year)
        await call.answer()

    async def spec_year_selection(self, message: Message, state: FSMContext):
        """Специальный расчет, получаем все данные по бренду"""

        year_str = message.text.strip()

        # Сохраняем в state
        await state.update_data({"year_str": year_str})

        # Просим ввести объём двигателя
        await message.answer(
            text="🔢 <b>Введите объём двигателя</b> в литрах "
            "(например, можно ввести <code>2.0</code>, <code>20</code> или <code>2000</code> — все варианты означают 2.0 литра):",
            parse_mode="HTML",
        )
        # Переходим в состояние waiting_for_engine
        await state.set_state(ManualSpecCalcStates.waiting_for_engine)

    async def spec_engine_input_spec(self, message: Message, state: FSMContext):
        """Специальный расчет, получаем объем и выводим расчет"""

        data = await state.get_data()

        engine_value = float(message.text.strip())
        year = int(data.get("year_str"))
        model = data.get("model_name")
        brand = data.get("brand")
        car_calculate: CalculateCar = await CalculateLogic().calculate(
            car_manufacture_year=year, engine_volume=engine_value
        )

        car: AuctionCar = AuctionCar(
            brand=brand.lower(), model=model, year=year, engine=engine_value
        )

        text = await self.bot.get_text(web_car=car, car_calculate=car_calculate)
        await message.answer(text, parse_mode="HTML")
        await state.clear()
