import datetime

from src.service.calculation.BaseCalculator import BasicCalculate
from src.service.calculation.models.CalculatorCarModel import (
    CalculateCar,
    CarTaxType,
)


class CalculateLogic(BasicCalculate):
    current_year = datetime.datetime.now().year

    async def __normalize_engine_volume(self, engine_volume: float) -> float:
        """
        Приводит значение объёма двигателя к кубическим сантиметрам (см³).

        Если значение меньше 10, предполагается, что оно указано в литрах,
        и умножается на 1000 (например, 4.4 → 4400).

        Если значение от 10 до 100, считается, что десятичная точка опущена
        (например, 44 вместо 4.4), поэтому делим на 10, а затем умножаем на 1000.

        Если значение 100 или больше, предполагается, что оно уже в см³.
        """
        if engine_volume < 10:
            # Например, 4.4 литра → 4.4 * 1000 = 4400 см³
            return engine_volume * 1000
        elif engine_volume < 100:
            # Например, 44 → (44 / 10) * 1000 = 4400 см³
            return (engine_volume / 10) * 1000
        else:
            # Значение уже в см³
            return engine_volume

    async def calculate(
        self,
        car_manufacture_year: int,
        engine_volume: int | float,
        car_price: int | float = 0,
    ) -> CalculateCar:

        car_age = self.current_year - car_manufacture_year
        engine_volume = await self.__normalize_engine_volume(engine_volume)

        if car_age < 3:
            # Здесь вызываем функцию для авто до 3 лет
            car_tax = await self.before_three_years(engine_volume, car_price)
            big_car_tax = await self.between_three_five_years(engine_volume)
            return CalculateCar(
                car_tax=car_tax,
                big_car_tax=big_car_tax if car_age == 2 else None,
                auction_tax=self.auction_tax,
                auction_button=self.auction_button,
                delivery=self.delivery,
                car_tax_type=CarTaxType.before_three_years,
            )
        elif car_age < 5:
            car_tax = await self.between_three_five_years(engine_volume)
            return CalculateCar(
                car_tax=car_tax,
                big_car_tax=None,
                auction_tax=self.auction_tax,
                auction_button=self.auction_button,
                delivery=self.delivery,
                car_tax_type=CarTaxType.between_three_five_years,
            )
        elif car_age == 5:
            # Машина ровно 5 лет – считаем оба варианта
            car_tax = await self.between_three_five_years(engine_volume)
            big_car_tax = await self.after_five_years(engine_volume)
            return CalculateCar(
                car_tax=car_tax,
                big_car_tax=big_car_tax,
                auction_tax=self.auction_tax,
                auction_button=self.auction_button,
                delivery=self.delivery,
            )

        else:
            # Для авто старше 5 лет
            big_car_tax = await self.after_five_years(engine_volume)
            return CalculateCar(
                car_tax=None,
                big_car_tax=big_car_tax,
                auction_tax=self.auction_tax,
                auction_button=self.auction_button,
                delivery=self.delivery,
                car_tax_type=CarTaxType.after_five_years,
            )
