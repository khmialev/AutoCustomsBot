import sys
from functools import lru_cache

from loguru import logger

from src.bot.settings import get_settings

LoguruLogger = logger.__class__


@lru_cache
def get_logger() -> LoguruLogger:
    """
    Returns a cached, globally configured logger instance.
    """
    settings = get_settings()
    log_level = "DEBUG" if settings.DEBUG else "INFO"

    logger.remove()

    logger.add(
        sys.stdout,
        level=log_level,
        format=_log_formatter,
        colorize=True,
    )

    logger.info("Logger configured with level: {}", log_level)
    return logger


def _log_formatter(record: dict) -> str:
    """
    Dynamically formats a log record.
    Adds a column for the class name if it was provided via bind().
    """
    format_string = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>\n"
    )

    if "name" in record["extra"]:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<cyan>{extra[name]: <30}</cyan> - "
            "<level>{message}</level>\n"
        )

    return format_string
