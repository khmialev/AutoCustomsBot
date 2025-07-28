import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from src.bot.dispatcher import create_dispatcher
from src.bot.settings import get_settings
from src.bot.startup.health_checks import HealthChecker
from src.infrastructure.database import create_engine, create_session_factory
from src.utils.logger import get_logger

logger = get_logger()
settings = get_settings()


async def main():
    """The main function which starts the bot."""

    # 1. Create long-lived dependencies
    logger.info("Creating long-lived dependencies...")
    engine = create_engine(settings=settings)
    session_factory = create_session_factory(engine=engine)
    logger.info("Dependencies created.")

    # 2. Perform health checks
    try:
        health_checker = HealthChecker(
            settings=settings,
            logger=logger,
            engine=engine,
        )
        await health_checker.run_all()
    except ConnectionError:
        logger.critical("Startup health checks failed. Bot is shutting down.")
        await engine.dispose()
        return

    # 3. Initialize Bot and Dispatcher
    bot = Bot(
        token=settings.TELEGRAM_API_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    dp = create_dispatcher(
        engine=engine,
        session_factory=session_factory,
    )

    logger.info("Bot is starting polling...")

    # 4. Start polling
    try:
        # todo: web sockets for prod
        await dp.start_polling(bot, settings=settings)
    finally:
        logger.info("Disposing database engine...")
        await engine.dispose()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
