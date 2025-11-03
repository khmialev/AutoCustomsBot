from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from src.bots.main_bot.handlers import all_routers
from src.core.database.middlewares.db_session import DatabaseMiddleware
from src.core.database.middlewares.exception_handler import (
    ExceptionHandlerMiddleware,
)


def create_dispatcher(
    engine: AsyncEngine,
    session_factory: async_sessionmaker,
) -> Dispatcher:
    """Creates and configures the aiogram Dispatcher."""

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.workflow_data["engine"] = engine
    dp.workflow_data["session_factory"] = session_factory

    # Register Middlewares
    dp.update.outer_middleware(ExceptionHandlerMiddleware())
    dp.update.middleware(DatabaseMiddleware(session_factory=session_factory))

    # Register Routers
    dp.include_routers(*all_routers)

    return dp
