from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.users import (
    add_user,
    user_exists,
)
from bot.utils.command import find_command_argument


class AuthMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        session: AsyncSession = data["session"]
        # state: FSMContext = data["state"]
        # bot: Bot = data["bot"]
        message: Message = event
        user = message.from_user

        if not user:
            return await handler(event, data)

        if not await user_exists(session, user.id):
            referrer_id = find_command_argument(message.text)
            logger.info(f"new user registration | user_id: {user.id} | message: {message.text}")
            await add_user(session=session, user=user, referrer_id=referrer_id)

        return await handler(event, data)
