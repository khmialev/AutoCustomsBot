from aiogram.fsm.context import FSMContext
from aiogram.types import Message


async def send_and_delete(
    message: Message,
    state: FSMContext,
    text: str,
    parse_mode=None,
    reply_markup=None,
):
    """Функция для удаления предыдущих сообщений из чата"""
    data = await state.get_data()
    if old_msg_id := data.get("last_bot_msg"):
        try:
            await message.bot.delete_message(message.chat.id, old_msg_id)
        except:
            pass

    new_msg = await message.answer(
        text, parse_mode=parse_mode, reply_markup=reply_markup
    )
    await state.update_data(last_bot_msg=new_msg.message_id)
