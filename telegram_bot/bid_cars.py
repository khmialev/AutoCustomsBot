import asyncio
import datetime

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from models.cars import AuctionCar
from telegram_bot.states.fsm_states import BidCarsCalcStates
from parsers.bidcars_parser import BidCars


class BidCarsUrlCalculator:
    def __init__(self, bot):
        self.bot = bot

        self.bot.dp.message.register(
            self.process_cmd_for_link_bid_cars, F.text == "Расчет по ссылке с BidCars"
        )
        # Хендлер, где пользователь вводит ссылку (waiting_for_url)
        self.bot.dp.message.register(
            self.process_url_input_bid_cars, BidCarsCalcStates.waiting_for_url
        )
        self.bot.dp.message.register(
            self.bot.process_car_price_for_under_3_years,
            BidCarsCalcStates.waiting_for_price_under_3_years,
        )

    async def process_cmd_for_link_bid_cars(self, message: Message, state: FSMContext):
        """Функция старта парса через ссылку copart"""
        await message.answer(
            "🟢 <b>Вставьте ссылку</b> на автомобиль (например):\n"
            "<code>https://bid.cars/ru/lot/0-41546549/2021-BMW-228i-Gran-Coupe-WBA73AK05M7H21100</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Я буду ждать вашу ссылку!",
            parse_mode="HTML",
        )
        await state.set_state(BidCarsCalcStates.waiting_for_url)

    async def process_url_input_bid_cars(self, message: Message, state: FSMContext):
        """
        Обрабатываем введенную пользователем ссылку с copart.
        Здесь можно добавить валидацию URL, дальнейшую обработку и т.д.
        """
        url = message.text
        if not url.startswith("http"):
            await message.answer(
                "❌ <b>Некорректный URL.</b> Попробуйте снова.\n"
                "(Ссылка должна начинаться с <code>http</code>)",
                parse_mode="HTML",
            )
            await state.clear()
            return

        await message.answer(
            f"✅ <b>Ссылка получена:</b> <code>{url}</code>\n" "Начинаю обработку...",
            parse_mode="HTML",
        )
        car = BidCars(bid_cars_url=url)
        bid_car = None
        for _ in range(3):
            bid_car: AuctionCar = await car.get_data()
            if not bid_car:
                car.use_proxy = True
                await car.close_session()
                await message.answer(
                    "🔴 Что то пошло не так. Жду 10 секунд и пробую ещё...",
                    parse_mode="HTML",
                )
                await asyncio.sleep(10)
                continue
            break

        if not bid_car:
            await message.answer(
                "❌ <b>Сервер так и не ответил.</b>\nПопробуйте позже.",
                parse_mode="HTML",
            )
            await state.clear()
            return

        await state.update_data(car=bid_car)
        year = datetime.datetime.now().year
        if year - bid_car.year < 3:
            await message.answer(
                "⚠️ <b>Без стоимости авто нельзя рассчитать таможенную пошлину</b>.\n"
                "Для машин младше 3 лет пошлина идёт как % от цены.\n\n"
                "Пожалуйста, введите предполагаемую стоимость авто (в $):",
                parse_mode="HTML",
            )
            await state.set_state(BidCarsCalcStates.waiting_for_price_under_3_years)

        else:
            await self.bot.process_final_car_data(
                message=message, auction_car=bid_car, state=state
            )
