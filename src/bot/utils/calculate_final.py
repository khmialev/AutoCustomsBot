from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto

from calculation.calculator import CalculateLogic
from models.CalculatorCarModel import CalculateCar
from parsers.AvParser import av_statistic
from parsers.models.CarModel import AuctionCar, AvStatisticCar
from src.bot.utils.TextGenerator import text_generator


async def process_final_car_data(
    message: Message,
    auction_car: AuctionCar,
    state: FSMContext,
    estimated_price: float = None,
):

    car_calculate: CalculateCar = await CalculateLogic().calculate(
        car_manufacture_year=auction_car.year,
        engine_volume=auction_car.engine,
        car_price=estimated_price,
    )
    av_statistic_car: AvStatisticCar = await av_statistic.run(
        brand=auction_car.brand,
        model=auction_car.model,
        year=auction_car.year,
    )

    text = await text_generator.get_text(
        web_car=auction_car,
        car_calculate=car_calculate,
        estimated_price=estimated_price,
        av_statistic_car=av_statistic_car,
    )

    if auction_car.images:
        try:
            media = [
                InputMediaPhoto(
                    media=auction_car.images[0], caption=text, parse_mode="HTML"
                )
            ] + [InputMediaPhoto(media=url) for url in auction_car.images[1:10]]
            await message.answer_media_group(media)
        except TelegramBadRequest:
            text = await text_generator.get_text(
                web_car=auction_car,
                car_calculate=car_calculate,
                estimated_price=estimated_price,
                msg_to_long=True,
                av_statistic_car=av_statistic_car,
            )
            await message.answer_photo(
                photo=auction_car.image,
                caption=text,
                parse_mode="HTML",
            )
        except:
            await message.answer_photo(
                photo=auction_car.image, caption=text, parse_mode="HTML"
            )

    elif auction_car.image:
        await message.answer_photo(
            photo=auction_car.image, caption=text, parse_mode="HTML"
        )
    else:
        await message.answer(text, parse_mode="HTML")
    await state.clear()
