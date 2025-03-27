from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database.database_connection import DataBaseConnection
from database.db_models import Car


class DataBaseService(DataBaseConnection):

    async def create_tables(self):
        async with self.async_engine.connect() as conn:
            await conn.run_sync(self.Base.metadata.create_all)
            await conn.commit()

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
