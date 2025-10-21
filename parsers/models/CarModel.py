from pydantic import BaseModel


class AuctionCar(BaseModel):
    brand: str
    model: str
    year: int
    engine_capacity: float | None = None
    engine_type: str = None
    url: str | None = None
    buy_now: int | None = None
    current_bid: int | None = None
    sales_status: str | None = None
    main_damage: str | None = None
    secondary_damage: str | None = None
    image: str | None = None
    images: list[str] = None
    odometer: str = None

    def engine_type_for_statistic(self):
        if self.engine_type == "GAS":
            self.engine_type = "1"
        elif self.engine_type == "DIESEL":
            self.engine_type = "5"


class AvAnalyticsCar(BaseModel):
    brand: str
    model: str
    generation: str
    year: int
    average_price: float
    average_sell_days: int


class AvStatisticCar(BaseModel):
    brand: str
    model: str
    generation: str
    year: str
    price_min: float
    price_max: float
    average_price: float
    count_cars: int
