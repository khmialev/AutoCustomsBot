from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from service.tracking_manager import TrackingManager
from telegram_bot.states.fsm_states import TrackingBidCars


class BidCarsTracking:
    def __init__(self, bot):
        self.bot = bot
        self.tracking_manager = TrackingManager()

        self.bot.dp.message.register(
            self.main_process, F.text == "Отслеживать авто с BidCars"
        )

        self.bot.dp.callback_query.register(
            self.process_brand_input,
            TrackingBidCars.waiting_for_model,
            F.data.in_(self.bot.car_brands),
        )

        self.bot.dp.callback_query.register(
            self.process_model_input, TrackingBidCars.waiting_for_year
        )

        self.bot.dp.callback_query.register(
            self.process_tracking, TrackingBidCars.waiting_for_generation
        )
        self.bot.dp.message.register(
            self.stop_tracking_command, F.text == "🛑 Остановить отслеживание"
        )

    async def main_process(self, message: Message, state: FSMContext):
        await state.clear()

        msg = await message.answer(
            "🟢 <b>СТАРТ ОТСЛЕЖИВАНИЯ</b>\n" "━━━━━━━━━━━━━━━━━━━━\n" "Выберите бренд:",
            parse_mode="HTML",
            reply_markup=await self.bot.keyboards.create_brands_keyboard(),
        )

        await state.update_data(tracking_message_id=msg.message_id)
        await state.set_state(TrackingBidCars.waiting_for_model)

    async def process_brand_input(self, call: CallbackQuery, state: FSMContext):
        brand = call.data.lower()
        await state.update_data(brand=brand)

        car_models = await self.bot.db.get_models(brand=brand)
        data = await state.get_data()
        msg_id = data["tracking_message_id"]

        text = (
            f"🟢 <b>СТАРТ ОТСЛЕЖИВАНИЯ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 Бренд: <b>{brand.upper()}</b>\n"
            f"Выберите модель:"
        )
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=msg_id,
            text=text,
            parse_mode="HTML",
            reply_markup=await self.bot.keyboards.create_models_keyboards(car_models),
        )
        await call.answer()
        await state.set_state(TrackingBidCars.waiting_for_year)

    async def process_model_input(self, call: CallbackQuery, state: FSMContext):
        model = call.data.lower().split(":")[-1]
        await state.update_data(model=model)

        data = await state.get_data()
        brand = data["brand"]
        msg_id = data["tracking_message_id"]

        generations = await self.bot.db.get_years(brand=brand, model=model)

        text = (
            f"🟢 <b>СТАРТ ОТСЛЕЖИВАНИЯ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 Бренд: <b>{brand.upper()}</b>\n"
            f"📌 Модель: <b>{model.upper()}</b>\n"
            f"Выберите поколение:"
        )
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=msg_id,
            text=text,
            parse_mode="HTML",
            reply_markup=await self.bot.keyboards.create_years_keyboard(generations),
        )
        await call.answer()
        await state.set_state(TrackingBidCars.waiting_for_generation)

    async def process_tracking(self, call: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        brand = data["brand"]
        model = data["model"]
        msg_id = data["tracking_message_id"]

        year_from, year_to = call.data.split("_")

        text = (
            f"🎯 <b>Отслеживание запущено!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 Бренд: <b>{brand.upper()}</b>\n"
            f"📌 Модель: <b>{model.upper()}</b>\n"
            f"📌 Года: <b>{year_from} - {year_to}</b>"
        )

        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=msg_id,
            text=text,
            parse_mode="HTML",
            reply_markup=None,
        )

        await state.clear()
        await call.answer()
        await self.tracking_manager.start_tracking(
            user_id=call.from_user.id,
            chat_id=call.message.chat.id,
            brand=brand,
            model=model,
            year_to=year_to,
            year_from=year_from,
            bot=call.bot,
        )
        await call.message.answer(
            "✅ Отслеживание запущено!",
            reply_markup=await self.bot.keyboards.create_main_keyboard(
                is_tracking=True
            ),
        )

    async def stop_tracking_command(self, message: Message):
        user_id = message.from_user.id

        if self.tracking_manager._is_tracking(user_id):
            await self.tracking_manager.stop_tracking(user_id)
            await message.answer(
                "❌ Отслеживание остановлено.",
                reply_markup=await self.bot.keyboards.create_main_keyboard(
                    is_tracking=False
                ),
            )
        else:
            await message.answer(
                "ℹ️ У вас нет активного отслеживания.",
                reply_markup=await self.bot.keyboards.create_main_keyboard(
                    is_tracking=False
                ),
            )
