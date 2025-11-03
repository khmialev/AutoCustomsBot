from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bots.main_bot.constants.emojis import LOCATION
from src.bots.main_bot.constants.texts import HANDLE_START_COMMAND
from src.bots.main_bot.keyboards.MainMenu import main_menu_keyboard
from src.core.database.repositories.repository_manager import RepositoryManager

router = Router(name="main-menu-router")


@router.message(
    Command("start"),
)
async def handle_start_command(
    message: Message, repo_manager: RepositoryManager
):
    user_id = message.from_user.id
    user = await repo_manager.users.get_by_user_id(user_id)
    if not user:
        user = await repo_manager.users.create(
            user_id=message.from_user.id,
            username=message.from_user.username,
        )
        await message.answer(
            f"Привет, {user.username or 'пользователь'}! Ты зарегистрирован ✅"
        )

    await message.answer(
        text=f"{LOCATION} {HANDLE_START_COMMAND}",
        reply_markup=await main_menu_keyboard(),
    )
