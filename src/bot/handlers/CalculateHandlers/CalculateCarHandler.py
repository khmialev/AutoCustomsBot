import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from parsers.BidCars import bidcars
from parsers.models.CarModel import AuctionCar
from src.bot.constants.emojis import CROSS, CHECK, WARNING
from src.bot.constants.texts import (
    START_CALCULATE,
    INCORRECT_URL,
    CORRECT_URL,
    INPUT_CAR_PRICE,
    INPUT_NUMBER,
    INCORRECT_CAR_DATA,
    NOT_CAR_DATA,
)
from src.bot.states.CalculationCustomsFeeStates import CalculateBidCarsStates
from src.bot.utils.CalculateFinal import process_final_car_data

router = Router(name="calculate-car-router")


@router.message(F.text == "📟 Сделать расчет")
async def start_calculate_bidcars(message: Message, state: FSMContext):
    # todo надо сделать проверку на подписку или мидлвар
    await message.answer(
        f"{CHECK} {START_CALCULATE}",
        parse_mode="HTML",
    )
    await state.set_state(CalculateBidCarsStates.waiting_for_url)


@router.message(CalculateBidCarsStates.waiting_for_url)
async def calculate_process(message: Message, state: FSMContext):
    url = message.text
    if not url.startswith("http"):
        text = f"{CROSS} {INCORRECT_URL}"
        await message.answer(text=text, parse_mode="HTML")
        await state.clear()
        return

    await message.answer(
        text=f"{CHECK} {CORRECT_URL.format(url=url)}",
        parse_mode="HTML",
    )

    bid_car: AuctionCar = await bidcars.get_data(url=url)
    if not bid_car:
        await message.answer(
            text=f"{CROSS} {NOT_CAR_DATA}",
            parse_mode="HTML",
        )
        await state.clear()
        return

    await state.update_data(car=bid_car)
    year = datetime.datetime.now().year
    if year - bid_car.year < 3:
        text = f"{WARNING} {INPUT_CAR_PRICE}"
        await message.answer(
            text=text,
            parse_mode="HTML",
        )
        await state.set_state(
            CalculateBidCarsStates.waiting_for_price_under_3_years
        )

    else:
        await process_final_car_data(
            message=message, auction_car=bid_car, state=state
        )


@router.message(CalculateBidCarsStates.waiting_for_price_under_3_years)
async def process_car_price_for_under_3_years(
    message: Message, state: FSMContext
):
    estimated_price = message.text.strip()
    try:
        car_price = float(estimated_price)
    except ValueError:
        text = f"{CROSS} {INPUT_NUMBER}"
        await message.answer(text=text)
        return

    data = await state.get_data()
    car = data.get("car")
    if not car:

        await message.answer(text=INCORRECT_CAR_DATA)
        await state.clear()
        return

    await process_final_car_data(
        message=message,
        auction_car=car,
        state=state,
        estimated_price=car_price,
    )
