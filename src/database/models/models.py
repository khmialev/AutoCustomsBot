from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import BaseIdModel


class CarModel(BaseIdModel):
    __tablename__ = "cars"

    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    generation: Mapped[Optional[str]] = mapped_column(String(100))
    year_from: Mapped[Optional[int]] = mapped_column(Integer)
    year_to: Mapped[Optional[int]] = mapped_column(Integer)
    price_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    price_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    average_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    count_cars: Mapped[Optional[int]] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint(
            "brand",
            "model",
            "generation",
            "year_from",
            "year_to",
            name="_car_uc",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<CarModel(id={self.id}, brand={self.brand}, model={self.model})>"
        )


class BrandModel(BaseIdModel):
    __tablename__ = "brands"

    brand: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<BrandModel(id={self.id}, brand='{self.brand}')>"


class UserModel(BaseIdModel):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_expires: Mapped[Optional[datetime]] = mapped_column(DateTime)

    trackings: Mapped[list["TrackingParamModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, user_id={self.user_id})>"


class TrackingParamModel(BaseIdModel):
    __tablename__ = "tracking"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    brand: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    year_from: Mapped[Optional[int]] = mapped_column(Integer)
    year_to: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="trackings"
    )

    def __repr__(self) -> str:
        return f"<TrackingParamModel(id={self.id}, brand='{self.brand}', model='{self.model}')>"


class BidCarTipModel(BaseIdModel):
    __tablename__ = "bid_cars_tips"

    data: Mapped[dict] = mapped_column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f"<BidCarTipModel(id={self.id})>"
