import asyncio
from urllib.parse import urlencode

from aiogram import Bot

from parsers.base_parser import BasicParser


class TrackingBidCarsParser(BasicParser):

    async def build_url(self, brand, model, year_from, year_to, count: bool):
        base_url = "https://bid.cars/app/search/request"
        params = {
            "search-type": "filters",
            "status": "All",
            "type": "Automobile",
            "make": brand,
            "model": model,
            "year-from": year_from,
            "year-to": year_to,
            "auction-type": "All",
        }
        if count:
            params.update({"count": "true"})
        return f"{base_url}?{urlencode(params)}"

    async def track_cars_for_user(
        self,
        bot: Bot,
        user_id,
        chat_id,
        brand,
        model,
        year_from,
        year_to,
        on_stop=None,
        # надо что-то думать с филтром бренд и модель потому что есть не совпадение https://bid.cars/app/search/toolbar-type/automobile может тут надо спарсить?
    ):
        seen_ids = set()
        while True:
            # count_cars = await self.playwright.get_data(  # получили сколько всего машин
            #     await self.build_url(
            #         brand=brand,
            #         model=model,
            #         year_from=year_from,
            #         year_to=year_to,
            #         count=True,
            #     )
            # )
            cars_data = (
                await self.playwright.get_data(  # получили машины на одной страницы
                    await self.build_url(
                        brand=brand,
                        model=model,
                        year_from=year_from,
                        year_to=year_to,
                        count=False,
                    )
                )
            )
            if not cars_data["data"]:
                await bot.send_message(
                    text=f"По данным {brand}, {model} ничего не нашли", chat_id=chat_id
                )
                if on_stop:
                    await on_stop(user_id=user_id)
                break

            for data in cars_data["data"]:
                # todo проверка если тачка уже продана то не надо
                # photo = data["img_large"][0]
                url = f"https://bid.cars/ru/lot/{data['lot']}"
                vin = data["vin"]
                if vin in seen_ids:
                    print(f"This vin {vin} already in set")
                    continue
                seen_ids.update(vin)
                final_bid = data.get("final_bid")
                if final_bid:
                    print(f"This car {url} sold")
                    continue
                seen_ids.add(vin)
                year = data["name"].split(" ")[0]
                engine = data["specs"]["engine_rendered"]
                current_bid = data["prebid_price"]
                buy_now = data["buy_now_price"]
                damage = data["primary_damage"]
                estimated_min = data["estimated_min"]
                estimated_max = data["estimated_max"]
                location = data["location"]
                odometer = str(round(int(data["odometer"]) * 1.60, 2))
                seller = data["seller_long"]
                status = data["start_code"]
                time_left_formatted = data["time_left_formatted"]

                text = await self.get_car_text(
                    brand=brand,
                    model=model,
                    year=year,
                    engine=engine,
                    current_bid=current_bid,
                    buy_now=buy_now,
                    damage=damage,
                    url=url,
                    estimated_min=estimated_min,
                    estimated_max=estimated_max,
                    location=location,
                    odometer=odometer,
                    seller=seller,
                    status=status,
                    time_left_formatted=time_left_formatted,
                )
                await bot.send_message(text=text, parse_mode="HTML", chat_id=chat_id)
                # await bot.send_photo(
                #     caption=text, photo=photo, parse_mode="HTML", chat_id=chat_id
                # )
            await asyncio.sleep(60)

    async def get_car_text(
        self,
        brand,
        model,
        year,
        engine,
        current_bid,
        buy_now,
        damage,
        url,
        estimated_min,
        estimated_max,
        location,
        odometer,
        seller,
        status,
        time_left_formatted,
    ) -> str:
        text = (
            f"🚘 <b>{brand} {model} {year}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 <b>Объем:</b> {engine or '—'} л\n"
            f"💰 <b>Ставка сейчас:</b> {current_bid or '—'}\n"
            f"💵 <b>Купить сейчас:</b> {buy_now or '—'}\n"
            f"📈 <b>Оценочная стоимость:</b> $ {estimated_min or '—'} - ${estimated_max or '—'}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💥 <b>Повреждения:</b> {damage or '—'}\n"
            f"📍 <b>Локация:</b> {location or '—'}\n"
            f"📊 <b>Пробег:</b> {odometer or '—'}\n"
            f"🏷 <b>Продавец:</b> {seller or '—'}\n"
            f"📌 <b>Статус:</b> {status or '—'}\n"
            f"⏳ <b>Время до начала торгов:</b> {time_left_formatted or '—'}"
        )
        if url:
            text += f'🔗 <a href="{ url}">Открыть лот</a>'
        return text
