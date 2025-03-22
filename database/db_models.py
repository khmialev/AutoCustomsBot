import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base


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
