from abc import ABC
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.base import Base

Model = TypeVar("Model", bound=Base)


class AbstractRepository(ABC, Generic[Model]):
    """
    An abstract base class for data access repositories.

    It provides a generic implementation of common CRUD operations.
    """

    def __init__(self, session: AsyncSession, model: Type[Model]):
        self._session = session
        self._model = model

    async def get(self, **filter_kwargs: Any) -> Model | None:
        """Retrieve a single record by filter criteria."""
        stmt = select(self._model).filter_by(**filter_kwargs)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, **filter_kwargs: Any) -> list[Model]:
        """Retrieve a list of records, optionally filtered."""
        stmt = select(self._model).filter_by(**filter_kwargs)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **data: Any) -> Model:
        """Create a new record."""
        stmt = insert(self._model).values(**data).returning(self._model)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update(
        self, filter_kwargs: dict[str, Any], update_kwargs: dict[str, Any]
    ) -> Model | None:
        """Update a record matching filter criteria."""
        stmt = (
            update(self._model)
            .filter_by(**filter_kwargs)
            .values(**update_kwargs)
            .returning(self._model)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, **filter_kwargs: Any) -> None:
        """Delete records matching filter criteria."""
        stmt = delete(self._model).filter_by(**filter_kwargs)
        await self._session.execute(stmt)
