import datetime
from models.CalculatorCarModel import CalculateCar
from parsers.models.CarModel import AuctionCar, AvAnalyticsCar, AvStatisticCar
from src.bot.constants.emojis import CAR, RAZOR, TRUCK, DOLLAR, WARNING, CROSS
from src.bot.constants.texts import (
    CAR_SOURCE,
    CAR_INFO,
    BUY_NOW,
    CURRENT_BID,
    SALES_STATUS,
    CAR_AUCTION_INFO,
    CAR_DAMAGE_MAIN,
    CAR_DAMAGE_SECONDARY,
    EXPENSES_HEADER,
    EXPENSES_ITEM,
    EXPECTED_PRICE,
    CUSTOMS_TAX_HEADER,
    CUSTOMS_TAX_ITEM,
    CUSTOMS_TOTAL,
    WARNING_3_YEARS,
    WARNING_5_YEARS,
    NOT_FOUND,
    MULTIPLE_FOUND_HEADER,
    MULTIPLE_FOUND_ITEM,
    FEES_UP_TO_THREE_YEARS,
    FEES_THREE_TO_FIVE_YEARS,
)
from src.bot.settings import get_settings

settings = get_settings()


class CarTextGenerator:
    def __init__(self):
        self.euro_usd = settings.EURO_USD

    async def get_text(
        self,
        web_car: AuctionCar,
        car_calculate: CalculateCar,
        av_analytics_car: list[AvAnalyticsCar],
        av_statistic_car: list[AvStatisticCar],
        estimated_price: float = None,
        msg_to_long: bool = False,
    ):

        lines = []

        # 1) Источник данных
        if web_car.url:
            lines.append(f"{CAR_SOURCE.format(url=web_car.url)}")

        # 2) Блок про автомобиль
        text = f"{CAR} { CAR_INFO.format(
                brand=web_car.brand.upper(),
                model=web_car.model.upper(),
                year=web_car.year,
                engine=web_car.engine_capacity,
            )}"
        lines.append(text)

        if not msg_to_long:
            auction_lines = []
            if web_car.buy_now:
                auction_lines.append(BUY_NOW.format(buy_now=web_car.buy_now))
            if web_car.current_bid:
                auction_lines.append(
                    CURRENT_BID.format(
                        timestamp=datetime.datetime.now().strftime(
                            "%d.%m.%Y %H:%M"
                        ),
                        current_bid=web_car.current_bid,
                    )
                )
            if web_car.sales_status:
                auction_lines.append(
                    SALES_STATUS.format(sales_status=web_car.sales_status)
                )

            if auction_lines:
                text = f"{RAZOR} {CAR_AUCTION_INFO.format(
                        buy_now="\n".join(auction_lines),
                        current_bid="",
                        sales_status="",
                    )}"
                lines.append(text)

        if not msg_to_long:
            if web_car.main_damage:
                lines.append(
                    CAR_DAMAGE_MAIN.format(main_damage=web_car.main_damage)
                )
            if web_car.secondary_damage:
                lines.append(
                    CAR_DAMAGE_SECONDARY.format(
                        secondary_damage=web_car.secondary_damage
                    )
                )

        # 5) Расходы
        lines.append(f"{TRUCK} {EXPENSES_HEADER}")
        lines.append(
            EXPENSES_ITEM.format(name="Доставка", value=car_calculate.delivery)
        )
        lines.append(
            EXPENSES_ITEM.format(
                name="Комиссия аукциона", value=car_calculate.auction_tax
            )
        )
        lines.append(
            EXPENSES_ITEM.format(
                name="Декларанты", value=car_calculate.declorants
            )
        )
        lines.append(
            EXPENSES_ITEM.format(
                name="Льготник", value=car_calculate.disabled_person
            )
        )
        lines.append(
            EXPENSES_ITEM.format(
                name="Кнопка", value=car_calculate.auction_button
            )
        )

        # 6) Предполагаемая стоимость покупки (если есть)
        if estimated_price:
            lines.append(EXPECTED_PRICE.format(estimated_price=estimated_price))

        header = (
            FEES_UP_TO_THREE_YEARS
            if estimated_price
            else FEES_THREE_TO_FIVE_YEARS
        )

        car_tax_value = (
            float(car_calculate.car_tax) * self.euro_usd
            if car_calculate.car_tax
            else float(car_calculate.big_car_tax) * self.euro_usd
        )
        lines.append(
            f"{DOLLAR} {header}"
            + CUSTOMS_TAX_ITEM.format(
                discounted=car_tax_value / 2, full=car_tax_value
            )
        )
        if car_calculate.car_tax:
            lines.append(
                CUSTOMS_TOTAL.format(
                    discounted_total=car_calculate.discounted_common_total(),
                    total=car_calculate.common_total(),
                )
            )
        else:
            lines.append(
                CUSTOMS_TOTAL.format(
                    discounted_total=car_calculate.discounted_big_total(),
                    total=car_calculate.big_total(),
                )
            )

        if datetime.datetime.now().year - web_car.year == 2 and estimated_price:
            lines.append(f"{WARNING} {WARNING_3_YEARS}")
        if datetime.datetime.now().year - web_car.year == 5:
            lines.append(f"{WARNING} {WARNING_5_YEARS}")

        # поудмай над статистикой!!!
        if not av_analytics_car:
            lines.append(
                f"{CROSS} {NOT_FOUND.format(brand=web_car.brand.upper(), model=web_car.model, year=web_car.year)}"
            )
        elif len(av_analytics_car) > 1:
            # Найдено несколько вариантов
            lines.append(f"{WARNING} {MULTIPLE_FOUND_HEADER}")
            for c in av_analytics_car:
                lines.append(
                    MULTIPLE_FOUND_ITEM.format(
                        brand=c.brand.upper(),
                        model=c.model.upper(),
                        generation=c.generation,
                        year=c.year,
                        average_price=c.average_price,
                        average_sell_days=c.average_sell_days,
                    )
                )
        if av_statistic_car:
            ...

        return "\n".join(lines)


text_generator = CarTextGenerator()
