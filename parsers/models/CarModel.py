from pydantic import BaseModel


class AuctionCar(BaseModel):
    brand: str
    model: str
    year: int
    engine: float | None = None
    url: str | None = None
    buy_now: int | None = None
    current_bid: int | None = None
    sales_status: str | None = None
    main_damage: str | None = None
    secondary_damage: str | None = None
    image: str | None = None
    images: list[str] = None


class AvStatisticCar(BaseModel):
    brand: str
    model: str
    generation: str
    year: int
    average_price: int
    average_sell_days: int
