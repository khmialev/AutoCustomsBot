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
        self.bot.dp.message.register(
            self.process_car_price_for_under_3_years,
            CopartCalcStates.waiting_for_price_under_3_years,
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
            await state.update_data(copart_car=copart_car)
            year = datetime.datetime.now().year
            if year - copart_car.year < 3:
                await message.answer(
                    "⚠️ <b>Без стоимости авто нельзя рассчитать таможенную пошлину</b>.\n"
                    "Для машин младше 3 лет пошлина идёт как % от цены.\n\n"
                    "Пожалуйста, введите предполагаемую стоимость авто (в $):",
                    parse_mode="HTML",
                )
                await state.set_state(CopartCalcStates.waiting_for_price_under_3_years)

            else:
                await self.bot.process_final_car_data(
                    message=message, auction_car=copart_car, state=state
                )
            break

    async def process_car_price_for_under_3_years(
        self, message: Message, state: FSMContext
    ):
        estimated_price = message.text.strip()
        try:
            car_price = float(estimated_price)
        except ValueError:
            await message.answer("❌ Пожалуйста, введите число (например, 15000).")
            return

        data = await state.get_data()
        copart_car = data.get("copart_car")
        if not copart_car:
            await message.answer("Данные о машине не найдены, начните заново.")
            await state.clear()
            return

        await self.bot.process_final_car_data(
            message=message,
            auction_car=copart_car,
            state=state,
            estimated_price=car_price,
        )
