import asyncio
from aiogram.types import InlineKeyboardButton
import aiogram
from aiogram.types import CallbackQuery
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import F, BaseMiddleware, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from cachetools import TTLCache
from sqlalchemy.ext.asyncio import AsyncSession

from bot.bot_controller import try_delete_message
from bot.services.users import get_language_code, set_language_code


class AskLanguageMiddleware(BaseMiddleware):

    def __init__(self) -> None:
        self._cached_futures: dict[int, asyncio.Future] = TTLCache(
            maxsize=10_000, ttl=2 * 24 * 60 * 60
        )
        self.router = Router()
        self.router.message.register(self.handle_response, F.data.regexp(r"^language:.+$"))

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        session: AsyncSession = data["session"]
        state: FSMContext = data["state"]
        message: Message = event
        bot: Bot = data["bot"]
        user = message.from_user

        if not user:
            return await handler(event, data)

        if await get_language_code(session, user.id) is not None:
            return await handler(event, data)

        # if already awaiting and there is a future
        if self._cached_futures.get(user.id):
            return await handler(event, data)
        # if not waiting for capcha and need to wait
        await self.ask_language(bot=bot, user_id=user.id, state=state)

        return await handler(event, data)

    async def ask_language(self, bot: Bot, user_id: int, state: FSMContext) -> None:
        future = asyncio.get_running_loop().create_future()
        self._cached_futures[user_id] = future
        await self.send_language_request(user_id=user_id, bot=bot, state=state)
        await future

    async def send_language_request(self, bot: Bot, user_id: int, state: FSMContext) -> None:
        text = _("Meet your language: ")
        markup = [
            [InlineKeyboardButton("Русский", callback_data="language:ru")],
            [InlineKeyboardButton("English", callback_data="language:en")],
        ]
        tempdata = await state.get_data()
        await try_delete_message(bot, user_id, tempdata.get("ex_message_id"))
        msg = await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=markup,
        )
        await state.update_data({"ex_message_id": msg.message_id})

    async def handle_response(self, query: CallbackQuery, session: AsyncSession, bot: Bot) -> None:
        user: aiogram.types.User = query.from_user
        language_code = query.data.split(":", 1)[1]
        await set_language_code(session, query.from_user.id, language_code)

        future = self._cached_futures.get(user.id)
        if future is None:
            return
        await future.set_result(True)
