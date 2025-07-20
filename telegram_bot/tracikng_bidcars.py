import asyncio

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from models.fsm_states import TrackingBidCars
from parsers.tracking_bid_cars_parser import TrackingBidCarsParser


class BidCarsTracking:
    def __init__(self, bot):
        self.bot = bot

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

    async def main_process(self, message: Message, state: FSMContext):
        await state.clear()

        msg = await message.answer(
            "🟢 <b>СТАРТ ОТСЛЕЖИВАНИЯ</b>\n" "━━━━━━━━━━━━━━━━━━━━\n" "Выберите бренд:",
            parse_mode="HTML",
            reply_markup=await self.bot._create_brands_keyboard(),
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
            reply_markup=await self.bot._create_models_keyboards(car_models),
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
            reply_markup=await self.bot._create_years_keyboard(generations),
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
        parser = TrackingBidCarsParser()
        # todo надо хранить такси с названием что бы потом сделат ькнопку и остнавлаивать их!!!
        asyncio.create_task(
            parser.track_cars_for_user(
                bot=call.bot,
                user_id=call.from_user.id,
                chat_id=call.message.chat.id,
                brand=brand,
                model=model,
                year_from=year_from,
                year_to=year_to,
            )
        )
        await call.answer()
        await state.clear()
