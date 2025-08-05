from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.constants.emojis import INFO
from src.bot.constants.static_texts import (
    FINISH_CUSTOM_FEES_HTML,
)
from src.bot.constants.texts import (
    START_SET_CUSTOM_FEES,
    DELIVERY_VIA_GEORGIA,
    DELIVERY_VIA_LITHUANIA,
    AUCTION_FEE,
    DECLARANTS_FEE,
    BENEFICIARY_FEE,
    CUSTOMS_DUTY,
    RECYCLING_FEE,
    AUCTION_PLAY_FEE,
)
from src.bot.states.CalculationCustomsFeeStates import CustomFeesStates
from src.bot.utils.DeletePreviousMessage import send_and_delete
from telegram_bot.keyboards.CalculateMenu import calculation_menu_keyboard

router = Router(name="calculate-set-fees-router")


@router.message(F.text == "🛠 Задать свои значения для расчета")
async def start_set_custom_fees(message: Message, state: FSMContext):
    await message.answer(
        text=f"{INFO} {START_SET_CUSTOM_FEES}",
        parse_mode="HTML",
    )
    text = DELIVERY_VIA_GEORGIA
    await send_and_delete(message=message, state=state, text=text)
    await state.set_state(CustomFeesStates.waiting_for_delivery_through_georgia)


@router.message(CustomFeesStates.waiting_for_delivery_through_georgia)
async def set_delivery_lithuania(message: Message, state: FSMContext):
    await state.update_data(delivery_georgia=float(message.text))
    text = DELIVERY_VIA_LITHUANIA
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(
        CustomFeesStates.waiting_for_delivery_through_lithuania
    )


@router.message(CustomFeesStates.waiting_for_delivery_through_lithuania)
async def set_auction_fee(message: Message, state: FSMContext):
    await state.update_data(delivery_lithuania=float(message.text))
    text = AUCTION_FEE
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_auction_fee)


@router.message(CustomFeesStates.waiting_for_auction_fee)
async def set_declarant_fee(message: Message, state: FSMContext):
    await state.update_data(auction_fee=float(message.text))
    text = DECLARANTS_FEE
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_declarant_fee)


@router.message(CustomFeesStates.waiting_for_declarant_fee)
async def set_beneficiary_fee(message: Message, state: FSMContext):
    await state.update_data(declarant_fee=float(message.text))
    text = BENEFICIARY_FEE
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_beneficiary_fee)


@router.message(CustomFeesStates.waiting_for_beneficiary_fee)
async def set_customs_duty(message: Message, state: FSMContext):
    await state.update_data(beneficiary_fee=float(message.text))
    text = CUSTOMS_DUTY
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_customs_duty)


@router.message(CustomFeesStates.waiting_for_customs_duty)
async def set_recycling_fee(message: Message, state: FSMContext):
    await state.update_data(customs_duty=float(message.text))
    text = RECYCLING_FEE
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_recycling_fee)


@router.message(CustomFeesStates.waiting_for_recycling_fee)
async def set_auction_play_fee(message: Message, state: FSMContext):
    await state.update_data(recycling_fee=float(message.text))
    text = AUCTION_PLAY_FEE
    await send_and_delete(message=message, state=state, text=text)

    await state.set_state(CustomFeesStates.waiting_for_auction_play_fee)


@router.message(CustomFeesStates.waiting_for_auction_play_fee)
async def finish_custom_fees(message: Message, state: FSMContext):
    await state.update_data(auction_play_fee=float(message.text))
    data = await state.get_data()

    # TODO: сохранить data в user_fees (БД), может если натыкл 0 то вывести дефолтные значения?
    text = FINISH_CUSTOM_FEES_HTML.format(**data)
    await send_and_delete(
        message=message,
        state=state,
        text=text,
        parse_mode="HTML",
        reply_markup=await calculation_menu_keyboard(),
    )

    await state.clear()
