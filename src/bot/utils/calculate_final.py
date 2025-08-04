from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto

from calculation.calculator import CalculateLogic
from models.CalculatorCarModel import CalculateCar

from parsers.AvAnalyticsParser import av_analytics
from parsers.AvStatisticParser import av_statistic, AvStatistic
from parsers.models.CarModel import AuctionCar, AvAnalyticsCar
from src.bot.utils.TextGenerator import text_generator


async def process_final_car_data(
    message: Message,
    auction_car: AuctionCar,
    state: FSMContext,
    estimated_price: float = None,
):

    car_calculate: CalculateCar = await CalculateLogic().calculate(
        car_manufacture_year=auction_car.year,
        engine_volume=auction_car.engine_capacity,
        car_price=estimated_price,
    )
    av_analytics_car: AvAnalyticsCar = await av_analytics.run(
        brand=auction_car.brand,
        model=auction_car.model,
        year=auction_car.year,
        engine_type=auction_car.engine_type,
        engine_capacity=auction_car.engine_capacity,
    )

    av_statistic_car: AvStatistic = await av_statistic.run_parser(
        brand=auction_car.brand,
        model=auction_car.model,
        year=auction_car.year,
    )

    text = await text_generator.get_text(
        web_car=auction_car,
        car_calculate=car_calculate,
        estimated_price=estimated_price,
        av_analytics_car=av_analytics_car,
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
                av_analytics_car=av_analytics_car,
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
