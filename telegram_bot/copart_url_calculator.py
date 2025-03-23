import asyncio
import datetime

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from parsers.copart_parser import CopartParser
from calculation.car_calculator import CalculateLogic
from models.cars import CalculateCar, AuctionCar
from models.fsm_states import CopartCalcStates


class CopartUrlCalculator:
    def __init__(self, bot):
        self.bot = bot

        self.bot.dp.message.register(
            self.process_cmd_for_link_copart, F.text == "Расчет по ссылке с copart"
        )
        # Хендлер, где пользователь вводит ссылку (waiting_for_url)
        self.bot.dp.message.register(
            self.process_url_input_copart, CopartCalcStates.waiting_for_url
        )

    async def process_cmd_for_link_copart(self, message: Message, state: FSMContext):
        """Функция старта парса через ссылку copart"""
        await message.answer(
            "🟢 <b>Вставьте ссылку</b> на автомобиль (например):\n"
            "<code>https://www.copart.com/lot/42034105/2021-honda-hr-v-ex-ma-freetown</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<b>ИЛИ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "<code>https://www.copart.com/lot/50086635</code>\n\n"
            "Я буду ждать вашу ссылку!",
            parse_mode="HTML",
        )
        await state.set_state(CopartCalcStates.waiting_for_url)

    async def process_url_input_copart(self, message: Message, state: FSMContext):
        # todo надо фиксить историю с куками
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
            return

        await message.answer(
            f"✅ <b>Ссылка получена:</b> <code>{url}</code>\n" "Начинаю обработку...",
            parse_mode="HTML",
        )
        copart_car = None
        car = CopartParser(copart_url=url)

        for _ in range(5):
            copart_car: AuctionCar = await car.get_data()
            if not copart_car:
                await car.close_session()
                await message.answer(
                    "🔴 Нет ответа от Copart. Жду 10 секунд и пробую ещё...",
                    parse_mode="HTML",
                )
                await asyncio.sleep(10)
                continue

            year = datetime.datetime.now().year
            if year - copart_car.year < 3:
                await message.answer(
                    "⚠️ <b>Без стоимости авто нельзя рассчитать таможенную пошлину</b>.\n"
                    "Для машин младше 3 лет пошлина идёт как % от цены.",
                    parse_mode="HTML",
                )
                # todo можно просить примерную стоимость
                return

            car_calculate: CalculateCar = await CalculateLogic().calculate(
                car_manufacture_year=copart_car.year, engine_volume=copart_car.engine
            )

            text = await self.bot.get_text(
                web_car=copart_car, car_calculate=car_calculate
            )

            if copart_car.image:
                await message.answer_photo(
                    photo=copart_car.image, caption=text, parse_mode="HTML"
                )
            else:
                await message.answer(text, parse_mode="HTML")

            break
        if not copart_car:
            await message.answer(
                "❌ <b>Сервер так и не ответил.</b>\nПопробуйте позже.",
                parse_mode="HTML",
            )
        await state.clear()
