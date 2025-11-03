from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.models import TrackingParamModel
from src.database.repositories.absctract_repository import AbstractRepository


class TrackingRepository(AbstractRepository[TrackingParamModel]):
    """Repository for managing tracking parameters."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, TrackingParamModel)

    async def count_by_user_id(self, user_id: int) -> int:
        """Подсчёт количества отслеживаний у пользователя."""
        stmt = select(func.count()).where(self._model.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_all_by_user_id(
        self, user_id: int
    ) -> list[TrackingParamModel]:
        """Получить все отслеживания пользователя."""
        stmt = select(self._model).where(self._model.user_id == user_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
