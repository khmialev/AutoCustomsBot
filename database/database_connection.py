from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import ASYNC_DATABASE_URL
from database.db_models import Base


class DataBaseConnection:
    """
    Базовый класс для получения сессии.
    Можно (но не обязательно) создавать здесь контекстный менеджер
    или хранить session как поле.
    """

    def __init__(self):
        self.Base = Base
        self.async_engine = create_async_engine(ASYNC_DATABASE_URL)
        self.async_session_local = async_sessionmaker(
            bind=self.async_engine, expire_on_commit=False
        )

    @property
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Создаём новую async-сессию и возвращаем её.
        """
        async with self.async_session_local() as session:
            yield session
