from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.repositories.abstract_manager import (
    AbstractRepositoryManager,
)


class OrmRepositoryManager(AbstractRepositoryManager):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def close(self) -> None:
        await self._session.close()
