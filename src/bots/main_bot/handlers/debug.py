from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.app.logger import get_logger

logger = get_logger()

router = Router(name="debug-router")


@router.message(Command("test_error"))
async def command_test_error(message: Message):
    """
    This handler intentionally raises an unhandled exception
    to test the ExceptionHandlerMiddleware.
    """

    logger.info("Executing /test_error command to trigger an exception.")
    result = 1 / 0  # noqa: F841
    await message.answer("This message should not appear.")
