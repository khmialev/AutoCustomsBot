from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from src.app.logger import LoguruLogger
from src.app.settings import Settings


class HealthChecker:
    """
    Performs startup health checks for all external dependencies.
    It receives pre-initialized clients to check their status.
    """

    def __init__(
        self,
        settings: Settings,
        logger: LoguruLogger,
        engine: AsyncEngine,
    ):
        self.settings = settings
        self.logger = logger
        self.engine = engine

        self.logger.info(f"{self.__class__.__name__} initialized.")

    async def _check_database_connection(self) -> None:
        """Performs a health check on the provided database engine."""

        self.logger.info("Checking database connection...")
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            self.logger.info("Database connection check passed.")
        except Exception as e:
            raise ConnectionError(f"Database health check failed: {e}")

    async def run_all(self) -> None:
        """Runs all configured health checks in sequence."""

        self.logger.info("Performing all startup health checks...")
        await self._check_database_connection()
        self.logger.info("All health checks passed successfully.")
