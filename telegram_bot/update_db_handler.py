import asyncio

from aiogram import F
from aiogram.types import Message, CallbackQuery


class UpdateDBHandler:
    def __init__(self, bot):
        self.bot = bot

        # Когда пользователь отправляет текст "Обновить БД с ценами (av)"
        self.bot.dp.message.register(
            self.update_db_menu, F.text == "Обновить БД с ценами (av.by)"
        )
        # При нажатии кнопки "Все бренды"
        self.bot.dp.callback_query.register(
            self.all_brands_callback, F.data == "all_brands"
        )
        # При нажатии кнопки "Один бренд"
        self.bot.dp.callback_query.register(self.brand_callback, F.data == "brand")
        # Если нужна кнопка остановки обновления
        self.bot.dp.callback_query.register(
            self.stop_update_callback, F.data == "stop_update"
        )
        self.bot.dp.callback_query.register(
            self.process_brand_input, F.data.in_(self.bot.car_brands)
        )

    async def update_db_menu(self, message: Message):
        """меню для выбора обновления БД, все машины или одна"""
        await message.answer(
            text=(
                "Хорошо! Теперь выбери действие для обновления базы данных с ценами:"
            ),
            reply_markup=await self.bot.keyboards.create_main_keyboard_for_udate_db(),
            parse_mode="HTML",
        )

    async def all_brands_callback(self, call: CallbackQuery):
        # Убираем клавиатуру из исходного сообщения
        await call.message.edit_reply_markup(reply_markup=None)
        self.bot.av_parser.stop_update = False
        total_brands = len(self.bot.car_brands)
        log_text = ""
        header_text = (
            "🔎 <b>Начинаю обновление всех брендов...</b>\n"
            "Это может занять несколько минут. Пожалуйста, подождите.\n\n"
        )

        progress_message = await call.message.answer(
            header_text + f"Прогресс: 0 / {total_brands} брендов",
            parse_mode="HTML",
            reply_markup=await self.bot.keyboards.stop_keyboard(),
        )

        success = 0
        for brand in self.bot.car_brands:
            # Даем небольшой интервал между обновлениями
            await asyncio.sleep(1)
            if self.bot.av_parser.stop_update:
                log_text += (
                    f"⏹️ <b>Обновление прервано пользователем.</b>\n"
                    f"Обновлено: {success} / {total_brands} брендов.\n\n"
                )
                await progress_message.edit_text(
                    header_text + log_text,
                    parse_mode="HTML",
                )
                break

            try:
                # Обновляем сообщение о текущем процессе
                await progress_message.edit_text(
                    header_text
                    + log_text
                    + f"⚠️ <b>Обновление бренда {brand.upper()}...</b>\n"
                    f"Осталось: {total_brands - success} брендов.\n",
                    parse_mode="HTML",
                    reply_markup=await self.bot.keyboards.stop_keyboard(),
                )
                # Запускаем парсер для данного бренда
                result = await self.bot.av_parser.run_parser(brand=brand)
                if not result:
                    log_text += (
                        f"⏹️ <b>Обновление прервано пользователем.</b>\n"
                        f"Обновлено: {success} / {total_brands} брендов.\n\n"
                    )
                    await progress_message.edit_text(
                        header_text + log_text,
                        parse_mode="HTML",
                    )
                    break

                # Добавляем информацию об успешном обновлении данного бренда
                log_text += f"✅ <b>Бренд {brand.upper()} успешно обновлён!</b>\n"
                success += 1
                await progress_message.edit_text(
                    header_text
                    + log_text
                    + f"Прогресс: {success} / {total_brands} брендов.\n",
                    parse_mode="HTML",
                    reply_markup=await self.bot.keyboards.stop_keyboard(),
                )
            except Exception as e:
                log_text += f"❌ <b>Ошибка обновления {brand.upper()}!</b>\n"
                await progress_message.edit_text(
                    header_text
                    + log_text
                    + f"Прогресс: {success} / {total_brands} брендов.\n",
                    parse_mode="HTML",
                    reply_markup=await self.bot.keyboards.stop_keyboard(),
                )
                continue
        else:
            await progress_message.edit_text(
                header_text + log_text + "🎉 <b>Обновление всех брендов завершено.</b>",
                parse_mode="HTML",
                reply_markup=await self.bot.keyboards.stop_keyboard(),
            )
        await call.answer()

    async def brand_callback(self, call: CallbackQuery):
        """старт парса одной машины с av"""
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(
            "✏️ <b>Выберите название бренда:</b> ",
            parse_mode="HTML",
            reply_markup=await self.bot.keyboards.create_brands_keyboard(),
        )
        await call.answer()

    async def process_brand_input(self, call: CallbackQuery):
        self.bot.av_parser.stop_update = False
        await call.message.edit_reply_markup(reply_markup=None)

        brand = call.data.lower()
        header_text = (
            f"✅ <b>Бренд принят:</b> <code>{brand.upper()}</code>\n"
            "Начинаю обновление цен..."
        )
        progress_message = await call.message.answer(
            text=header_text,
            parse_mode="HTML",
            reply_markup=await self.bot.keyboards.stop_keyboard(),
        )
        try:
            await self.bot.av_parser.run_parser(brand)
            if self.bot.av_parser.stop_update:
                await progress_message.edit_text(
                    text=(
                        f"{header_text}\n" "⏹️ <b>Обновление прервано пользователем.</b>"
                    ),
                    reply_markup=None,
                    parse_mode="HTML",
                )
                return
            await call.message.answer(
                f"✅ <b>Успешно обновили цены</b> для бренда: <b>{brand}</b>!",
                parse_mode="HTML",
            )
        except:
            await call.message.answer(
                f"❌ <b>Ошибка при обновлении</b> для бренда: <b>{brand}</b>.",
                parse_mode="HTML",
            )

    async def stop_update_callback(self, call: CallbackQuery):
        """
        Остановка обновления базы данных.
        """
        self.bot.av_parser.stop_update = True
