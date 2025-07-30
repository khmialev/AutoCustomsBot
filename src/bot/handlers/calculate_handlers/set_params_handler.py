from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.bot.states.calculation_customs_fee_states import CustomFeesStates
from src.bot.utils.delete_previous_message import send_and_delete
from telegram_bot.keyboards.calculate_menu import calculation_menu_keyboard

router = Router(name="calculate-set-fees-router")

# удаляю предыдущие сообщения, а может не надо?


@router.message(F.text == "🛠 Задать свои значения для расчета")
async def start_set_custom_fees(message: Message, state: FSMContext):
    await message.answer(
        "ℹ️ <b>Информация:</b>\n"
        "Если вы введёте <b>0</b> на любом шаге, "
        "бот использует <i>значения по умолчанию</i>.\n\n",
        parse_mode="HTML",
    )
    text = "Введите стоимость доставки через Грузию ($):"
    await send_and_delete(message=message, state=state, text=text)
    await state.set_state(CustomFeesStates.waiting_for_delivery_through_georgia)


@router.message(CustomFeesStates.waiting_for_delivery_through_georgia)
async def set_delivery_lithuania(message: Message, state: FSMContext):
    await state.update_data(delivery_georgia=float(message.text))
    text = "Введите стоимость доставки через Литву ($):"
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(
        CustomFeesStates.waiting_for_delivery_through_lithuania
    )


@router.message(CustomFeesStates.waiting_for_delivery_through_lithuania)
async def set_auction_fee(message: Message, state: FSMContext):
    await state.update_data(delivery_lithuania=float(message.text))
    text = "Введите комиссию аукциона ($):"
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_auction_fee)


@router.message(CustomFeesStates.waiting_for_auction_fee)
async def set_declarant_fee(message: Message, state: FSMContext):
    await state.update_data(auction_fee=float(message.text))
    text = "Введите услуги декларанта ($):"
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_declarant_fee)


@router.message(CustomFeesStates.waiting_for_declarant_fee)
async def set_beneficiary_fee(message: Message, state: FSMContext):
    await state.update_data(declarant_fee=float(message.text))
    text = "Введите услуги льготника ($):"
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_beneficiary_fee)


@router.message(CustomFeesStates.waiting_for_beneficiary_fee)
async def set_customs_duty(message: Message, state: FSMContext):
    await state.update_data(beneficiary_fee=float(message.text))
    text = "Введите таможенный сбор ($):"
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_customs_duty)


@router.message(CustomFeesStates.waiting_for_customs_duty)
async def set_recycling_fee(message: Message, state: FSMContext):
    await state.update_data(customs_duty=float(message.text))
    text = "Введите утилизационный сбор ($):"
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_recycling_fee)


@router.message(CustomFeesStates.waiting_for_recycling_fee)
async def set_auction_play_fee(message: Message, state: FSMContext):
    await state.update_data(recycling_fee=float(message.text))
    text = "Введите услуги игры на аукционе ($):"
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_auction_play_fee)


@router.message(CustomFeesStates.waiting_for_auction_play_fee)
async def finish_custom_fees(message: Message, state: FSMContext):
    await state.update_data(auction_play_fee=float(message.text))
    data = await state.get_data()

    # TODO: сохранить data в user_fees (БД), может если натыкл 0 то вывести дефолтные значения?
    text = (
        "✅ <b>Ваши значения сохранены:</b>\n"
        f"🚢 Доставка через Грузию: {data['delivery_georgia']}$\n"
        f"🚢 Доставка через Литву: {data['delivery_lithuania']}$\n"
        f"💳 Комиссия аукциона: {data['auction_fee']}$\n"
        f"📄 Услуги декларанта: {data['declarant_fee']}$\n"
        f"👤 Льготник: {data['beneficiary_fee']}$\n"
        f"🏛 Таможенный сбор: {data['customs_duty']}$\n"
        f"♻️ Утилизационный сбор: {data['recycling_fee']}$\n"
        f"🎮 Игра на аукционе: {data['auction_play_fee']}$"
    )
    await send_and_delete(
        message=message,
        state=state,
        text=text,
        parse_mode="HTML",
        reply_markup=await calculation_menu_keyboard(),
    )

    await state.clear()
