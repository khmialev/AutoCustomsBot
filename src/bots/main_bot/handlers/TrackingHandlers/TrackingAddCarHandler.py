from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.bots.main_bot.keyboards.MainMenu import main_menu_keyboard
from src.bots.main_bot.keyboards.TrackingMenu import (
    create_brands_keyboard_bidcars,
    create_models_keyboards_bidcars,
    create_years_keyboard_bidcars,
)
from src.bots.main_bot.states.TrackingStates import TrackingBidCars
from src.core.database.repositories.repository_manager import RepositoryManager

router = Router(name="tracking-add-router")


@router.message(F.text == "➕ Добавить авто")
async def add_car(
    message: Message, state: FSMContext, repo_manager: RepositoryManager
):
    MAX_TRACKINGS_PER_USER = 1
    user = await repo_manager.users.get_by_user_id(user_id=message.from_user.id)
    current_count = await repo_manager.tracking.count_by_user_id(
        user_id=user.id
    )

    if current_count >= MAX_TRACKINGS_PER_USER:
        user_trackings = await repo_manager.tracking.get_all_by_user_id(
            user_id=user.id
        )

        tracks_list = "\n".join(
            [
                f"📌 {t.brand} {t.model} ({t.year_from}-{t.year_to})"
                for t in user_trackings
            ]
        )

        await message.answer(
            f"⚠️ Превышен лимит отслеживаний ({MAX_TRACKINGS_PER_USER})!\n\n"
            f"Вот твои активные:\n{tracks_list}\n\n"
            f"❌ Удали одно из них, чтобы добавить новое.",
            parse_mode="HTML",
        )
        return

    await message.answer(
        "Введите данные автомобиля для добавления...",
    )
    msg = await message.answer(
        "🟢 <b>СТАРТ ОТСЛЕЖИВАНИЯ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Выберите бренд:",
        parse_mode="HTML",
        reply_markup=await create_brands_keyboard_bidcars(),
    )
    await state.update_data(tracking_message_id=msg.message_id)
    await state.set_state(TrackingBidCars.waiting_for_model)


@router.callback_query(StateFilter(TrackingBidCars.waiting_for_model))
async def process_model_input(call: CallbackQuery, state: FSMContext):
    brand = call.data.split(":")[-1]
    await state.update_data(brand=brand)

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


@router.callback_query(StateFilter(TrackingBidCars.waiting_for_year))
async def process_year_input(call: CallbackQuery, state: FSMContext):
    model = call.data.split(":")[-1]
    await state.update_data(model=model)

    data = await state.get_data()
    brand = data["brand"]
    msg_id = data["tracking_message_id"]

    text = (
        f"🟢 <b>СТАРТ ОТСЛЕЖИВАНИЯ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Бренд: <b>{brand}</b>\n"
        f"📌 Модель: <b>{model}</b>\n"
        f"Выберите поколение:"
    )
    await call.bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=msg_id,
        text=text,
        parse_mode="HTML",
        reply_markup=await create_years_keyboard_bidcars(
            brand=brand, model=model
        ),
    )
    await call.answer()
    await state.set_state(TrackingBidCars.waiting_for_generation)


@router.callback_query(StateFilter(TrackingBidCars.waiting_for_generation))
async def process_add_to_db_params_for_tracking(
    call: CallbackQuery, state: FSMContext, repo_manager: RepositoryManager
):
    data = await state.get_data()
    brand = data["brand"]
    model = data["model"]
    year_from = call.data.split("-")[0].strip()
    year_to = call.data.split("-")[1].strip()
    msg_id = data["tracking_message_id"]

    if "all" in call.data:
        data = call.data.split(":")
        year_from = data[-2]
        year_to = data[-1]

    user = await repo_manager.users.get_by_user_id(user_id=call.from_user.id)
    await repo_manager.tracking.create(
        user_id=user.id,
        brand=brand,
        model=model,
        year_from=int(year_from),
        year_to=int(year_to),
        is_active=True,
    )

    text = (
        f"🎯 <b>Добавлено отслеживание!</b>\n"
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

    await call.message.answer(
        "Главное меню",
        reply_markup=await main_menu_keyboard(),
    )
