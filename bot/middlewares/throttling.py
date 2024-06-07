from __future__ import annotations
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from cachetools import TTLCache

from bot.core.config import settings


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = settings.RATE_LIMIT) -> None:
        self.cache = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        chat_id = data["event_chat"].id
        if chat_id in self.cache:
            return None
        self.cache[chat_id] = None
        return await handler(event, data)
