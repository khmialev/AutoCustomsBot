import traceback
from html import escape
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramAPIError
from aiogram.types import TelegramObject, Update

from src.bot.constants import emojis
from src.bot.exceptions.base import BaseAppException
from src.bot.settings import Settings
from src.utils.logger import get_logger

logger = get_logger()

TELEGRAM_MAX_MESSAGE_LENGTH = 4096
RESERVED_CHARS_FOR_HEADER = 500
MAX_TRACEBACK_LENGTH = TELEGRAM_MAX_MESSAGE_LENGTH - RESERVED_CHARS_FOR_HEADER


class ExceptionHandlerMiddleware(BaseMiddleware):
    """
    Middleware to catch and handle exceptions.

    This middleware intercepts custom application exceptions (BaseAppException subclasses)
    and all other unhandled errors, providing user-friendly feedback and
    detailed logs for developers.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)

        except BaseAppException as e:
            logger.info(f"Handled {e.__class__.__name__}: {e.message}")

            message_text = f"{emojis.ICON_WARNING} {e.message}"

            if isinstance(event, Update) and event.message:
                await event.message.answer(text=message_text)
            elif isinstance(event, Update) and event.callback_query:
                await event.callback_query.answer()
                await event.callback_query.message.answer(text=message_text)

            return

        except Exception as e:
            logger.exception(
                f"An unhandled {e.__class__.__name__} occurred: {e}"
            )

            settings: Settings = data["settings"]

            await self._notify_admin(data, event, settings, e)
            await self._notify_user(event)

            return

    @staticmethod
    async def _notify_admin(
        data: Dict[str, Any],
        event: TelegramObject,
        settings: Settings,
        exc: Exception,
    ):
        """Sends a detailed error report to the admin."""

        if not settings.TELEGRAM_ADMIN_ID:
            logger.warning("TELEGRAM_ADMIN_ID not set, skipping error report.")
            return

        try:
            user_info = "User: N/A"
            if event.message:
                user = event.message.from_user
                user_info = (
                    f"User: {user.id} (@{user.username or 'no_username'})"
                )
            elif event.callback_query:
                user = event.callback_query.from_user
                user_info = (
                    f"User: {user.id} (@{user.username or 'no_username'})"
                )

            tb_str = traceback.format_exc()

            error_message = (
                f"{emojis.ICON_POLICE_LIGHT} <b>Unhandled Exception!</b> {emojis.ICON_POLICE_LIGHT}\n\n"
                f"<b>{user_info}</b>\n\n"
                f"<b>Error:</b> {escape(str(exc))}"
            )

            if len(error_message) + len(tb_str) < TELEGRAM_MAX_MESSAGE_LENGTH:
                full_message = (
                    f"{error_message}\n\n"
                    f"<pre><code class='language-python'>{escape(tb_str)}</code></pre>"
                )
                await data["bot"].send_message(
                    chat_id=settings.TELEGRAM_ADMIN_ID,
                    text=full_message,
                    parse_mode="HTML",
                )

            else:
                await data["bot"].send_message(
                    chat_id=settings.TELEGRAM_ADMIN_ID,
                    text=error_message,
                    parse_mode="HTML",
                )

                truncated_tb = escape(tb_str[-MAX_TRACEBACK_LENGTH:])

                final_tb_message = (
                    f"<b>Traceback (last {MAX_TRACEBACK_LENGTH} chars):</b>\n"
                    f"<pre><code class='language-python'>...{truncated_tb}</code></pre>"
                )

                await data["bot"].send_message(
                    chat_id=settings.TELEGRAM_ADMIN_ID,
                    text=final_tb_message,
                    parse_mode="HTML",
                )

            logger.info(
                f"Successfully sent error report to admin {settings.TELEGRAM_ADMIN_ID}"
            )

        except TelegramAPIError as e:
            logger.error(
                f"Failed to send error report to admin via Telegram API: {e}"
            )
        except Exception as e:
            logger.exception(
                f"An unexpected error occurred within _notify_admin: {e}"
            )

    @staticmethod
    async def _notify_user(event: TelegramObject):
        """Sends a generic error message to the user."""

        user_message = (
            "An unexpected error occurred. We have been notified and are working to fix it. "
            "Please try again later."
        )
        try:
            if isinstance(event, Update) and event.message:
                await event.message.answer(text=user_message)
            elif isinstance(event, Update) and event.callback_query:
                await event.callback_query.answer()
                await event.callback_query.message.answer(text=user_message)
        except Exception:
            logger.exception("Failed to send the error message to the user.")
