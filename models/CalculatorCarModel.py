from typing import Optional
from pydantic import BaseModel
from src.bot.settings import get_settings

settings = get_settings()


class CalculateCar(BaseModel):
    car_tax: Optional[float] = None
    big_car_tax: Optional[float] = None
    auction_tax: int
    auction_button: int
    delivery: int
    euro_usd: float = settings.EURO_USD
    declorants: int = settings.DECLARANTS
    disabled_person: int = (
        settings.DISABLED_PERSON
    )  # инвалид - пока не использую

    def fixed_costs(self) -> float:
        return sum(
            (
                self.auction_button,
                self.auction_tax,
                self.delivery,
                self.declorants,
            )
        )

    def common_total(self) -> Optional[float]:
        if self.car_tax is None:
            return None
        return self.car_tax * self.euro_usd + self.fixed_costs()

    def discounted_common_total(self) -> Optional[float]:
        if self.car_tax is None:
            return None
        return (
            (self.car_tax * self.euro_usd) / 2
            + self.fixed_costs()
            + self.disabled_person
        )

    def big_total(self) -> Optional[float]:
        if self.big_car_tax is None:
            return None
        return self.big_car_tax * self.euro_usd + self.fixed_costs()

    def discounted_big_total(self) -> Optional[float]:
        if self.big_car_tax is None:
            return None
        return (
            (self.big_car_tax * self.euro_usd) / 2
            + self.fixed_costs()
            + self.disabled_person
        )
