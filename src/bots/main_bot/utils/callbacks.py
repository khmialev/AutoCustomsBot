from typing import Iterable

from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.bot.constants.lexicon import FEATURE_IN_DEVELOPMENT


def register_dev_placeholders(router: Router, callbacks: Iterable[str]):
    """
    Registers a placeholder handler for a list of callback data.

    This utility helps to quickly stub unimplemented features by attaching
    a generic "in development" handler to multiple callback queries at once.

    :param router: The aiogram Router to which the handler will be attached.
    :param callbacks: An iterable of callback data strings to handle.
    """

    @router.callback_query(F.data.in_(callbacks))
    async def handle_placeholder_callback(callback: CallbackQuery):
        """
        A generic placeholder handler that notifies the user
        that the feature is under development.
        """

        await callback.answer(text=FEATURE_IN_DEVELOPMENT, show_alert=True)


def register_ignore_handler(router: Router):
    """
    Registers a handler for 'ignore' callbacks.
    This is used for non-clickable buttons, like page indicators.
    It answers the callback to remove the loading state and does nothing else.

    :param router: The aiogram Router to attach the handler to.
    """

    @router.callback_query(F.data == "ignore")
    async def handle_ignore_callback(callback: CallbackQuery):
        await callback.answer()
