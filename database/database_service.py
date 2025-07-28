import asyncio

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database.database_connection import DataBaseConnection
from database.db_models import Car, BidCarsTips


class DataBaseService(DataBaseConnection):

    async def create_tables(self):
        async with self.async_engine.connect() as conn:
            await conn.run_sync(self.Base.metadata.create_all)
            await conn.commit()

    async def get_years(self, brand: str, model: str):
        async for session in self.get_session:
            stmt = (
                select(Car.generation, Car.year_from, Car.year_to)
                .where(Car.brand == brand, Car.model == model)
                .order_by(Car.year_from)
            )
            result = await session.execute(stmt)
            rows = result.all()
            return [
                {
                    "generation": row.generation,
                    "year_from": row.year_from,
                    "year_to": row.year_to,
                }
                for row in rows
            ]

    async def save_car_data(self, car_data):
        async for session in self.get_session:
            stmt = (
                insert(Car)
                .values(**car_data)
                .on_conflict_do_update(
                    index_elements=[
                        "brand",
                        "model",
                        "generation",
                        "year_from",
                        "year_to",
                    ],
                    set_=car_data,
                )
            )
            await session.execute(stmt)
            await session.commit()

    async def get_car_price(self, brand, model, year) -> list[Car] | Car | None:
        async for session in self.get_session:
            stmt = (
                select(Car)
                .where(Car.brand == brand.lower())
                .where(Car.model == model.lower())
                # year_from включительно
                .where(Car.year_from <= year)
                # year_to НЕ включительно
                .where(Car.year_to >= year)
            )
            # Если хотим получить одну запись (или None, если не нашлось)
            result = await session.execute(stmt)
            cars = result.scalars().all()

            if not cars:
                # Вообще ничего не найдено
                return None
            elif len(cars) == 1:
                # Нашлась ровно одна запись
                return cars[0]
            else:
                # Несколько записей — возвращаем все
                return cars

    async def get_models(self, brand: str):
        async for session in self.get_session:
            # Получаем DISTINCT по Car.model
            stmt = select(Car.model).where(Car.brand == brand).distinct()
            result = await session.execute(stmt)
            # Получаем список уникальных названий моделей
            models = [row[0] for row in result.all()]
            return models

    async def save_json(self, cars_json):
        async for session in self.get_session:
            result = await session.execute(select(BidCarsTips).limit(1))
            record = result.scalar_one_or_none()

            if record:
                record.data = cars_json  # обновляем JSON
            else:
                session.add(BidCarsTips(data=cars_json))  # если нет — добавляем

            await session.commit()

    async def get_json(self):
        async for session in self.get_session:
            result = await session.execute(
                select(BidCarsTips).order_by(BidCarsTips.id.desc()).limit(1)
            )
            record = result.scalar_one_or_none()
            return record.data if record else None
