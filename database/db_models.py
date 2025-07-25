import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    UniqueConstraint,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    generation = Column(String(100))
    year_from = Column(Integer)
    year_to = Column(Integer)
    price_min = Column(Numeric(10, 2))
    price_max = Column(Numeric(10, 2))
    average_price = Column(Numeric(10, 2))
    count_cars = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "brand", "model", "generation", "year_from", "year_to", name="_car_uc"
        ),
    )

    def __repr__(self):
        return f"<Car(brand={self.brand}, model={self.model}, year={self.generation})>"


class Brands(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True)
    brand = Column(String(100), nullable=False)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)  # Telegram user_id
    username = Column(String, nullable=True)  # Telegram username
    is_active = Column(Boolean, default=True)  # Активен ли бот у пользователя
    is_subscribed = Column(Boolean, default=False)  # Платная подписка
    subscription_expires = Column(DateTime, nullable=True)  # Когда истекает подписка

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # связь: один пользователь → много отслеживаний
    trackings = relationship(
        "TrackingParams", back_populates="user", cascade="all, delete-orphan"
    )


class TrackingParams(Base):
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year_from = Column(Integer, nullable=True)
    year_to = Column(Integer, nullable=True)

    is_active = Column(
        Boolean, default=True
    )  # можно остановить конкретное отслеживание

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("Users", back_populates="trackings")
