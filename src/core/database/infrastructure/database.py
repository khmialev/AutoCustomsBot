from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.app.logger import get_logger
from src.app.settings import Settings

logger = get_logger()


def create_engine(settings: Settings) -> AsyncEngine:
    """Creates an async engine instance."""

    logger.info("Creating database engine...")
    engine_link = settings.get_db_engine_link()
    if not engine_link:
        raise RuntimeError("Database connection link is not configured.")
    return create_async_engine(engine_link)


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Creates a session factory."""

    logger.info("Creating database session factory...")
    return async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
