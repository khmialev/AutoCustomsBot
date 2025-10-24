from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.bot.services.TrackingManager import tracking_manager
from src.bot.states.TrackingStates import TrackingBidCars
from telegram_bot.keyboards.MainMenu import main_menu_keyboard
from telegram_bot.keyboards.TrackingMenu import create_brands_keyboard_bidcars, create_models_keyboards_bidcars, \
    create_years_keyboard_bidcars

router = Router(name="tracking-add-router")


@router.message(F.text == "➕ Добавить авто", )
async def add_car_get_model(message: Message, state:FSMContext):
    sent_message = await message.answer(
        text="Введите данные автомобиля для отслеживания",
        reply_markup=await create_brands_keyboard_bidcars()

    )
    await state.update_data(tracking_message_id=sent_message.message_id)
    await state.set_state(TrackingBidCars.waiting_for_model)


@router.callback_query(TrackingBidCars.waiting_for_model,  F.data.startswith("brand:"))
async def get_year( call: CallbackQuery, state: FSMContext):
    brand = call.data.split(":")[-1]
    await state.update_data(brand=brand)

    # car_models = await self.bot.db.get_models(brand=brand)
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
        reply_markup=await create_models_keyboards_bidcars(brand=brand),
    )
    await call.answer()
    await state.set_state(TrackingBidCars.waiting_for_year)

@router.callback_query(TrackingBidCars.waiting_for_year)
async def get_generation(call: CallbackQuery, state: FSMContext):
    model = call.data.split(":")[-1]
    await state.update_data(model=model)

    data = await state.get_data()
    brand = data["brand"]
    msg_id = data["tracking_message_id"]

    # generations = await self.bot.db.get_years(brand=brand, model=model)

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
        reply_markup=await create_years_keyboard_bidcars(data=data),
    )
    await call.answer()
    await state.set_state(TrackingBidCars.waiting_for_generation)


@router.callback_query(TrackingBidCars.waiting_for_generation)
async def process_tracking(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    brand = data["brand"]
    model = data["model"]
    msg_id = data["tracking_message_id"]

    if "all" in call.data:
        data = call.data.split(":")
        year_from = data[-2]
        year_to = data[-1]
    else:
        year_from, year_to = call.data.split(":")

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
    await tracking_manager.start_tracking(
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
        reply_markup=await main_menu_keyboard(),
    )

