from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.core.database.repositories.repository_manager import RepositoryManager


class DatabaseMiddleware(BaseMiddleware):
    """
    This middleware provides a database session and repository manager
    to the handlers.
    """

    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_factory() as session:
            async with RepositoryManager(session=session) as manager:
                data["repo_manager"] = manager
                return await handler(event, data)
