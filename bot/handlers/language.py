from aiogram import F, Router, types, Bot
import aiogram
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from bot.bot_controller import send_message, try_delete_message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.users import set_language_code

router = Router(name="language")


@router.message(Command(commands=["language"]))
async def on_message(message: types.Message, bot: Bot, state: FSMContext) -> None:
    await state.set_state()
    await send_language(user_id=message.from_user.id, bot=bot, state=state)


async def send_language(bot: Bot, user_id: str, state: FSMContext) -> None:
    tempdata = await state.get_data()

    text = _("<b>Meet</b> your language: ")

    keyboard = [
        [InlineKeyboardButton(text="Русский", callback_data="language:ru")],
        [InlineKeyboardButton(text="English", callback_data="language:en")],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await try_delete_message(bot, user_id, tempdata.get("ex_message_id"))
    msg = await send_message(
        bot=bot,
        chat_id=user_id,
        text=text,
        reply_markup=markup,
    )
    await state.update_data({"ex_message_id": msg.message_id})


@router.callback_query(F.data.regexp(r"^language:"))
async def handle_response(
    query: CallbackQuery, bot: Bot, session: AsyncSession, state: FSMContext
) -> None:
    user: aiogram.types.User = query.from_user
    language_code = query.data.split(":", 1)[1]
    await set_language_code(session, query.from_user.id, language_code)

    from .menu import send_menu

    return await send_menu(bot=bot, session=session, user_id=user.id, state=state)
