"""1. Get all texts
pybabel extract --input-dirs=. -o bot/locales/messages.pot --project=messages.

2. Init translations
pybabel init -i bot/locales/messages.pot -d bot/locales -D messages -l en
pybabel init -i bot/locales/messages.pot -d bot/locales -D messages -l ru
pybabel init -i bot/locales/messages.pot -d bot/locales -D messages -l uk

3. Compile translations
pybabel compile -d bot/locales -D messages --statistics

pybabel update -i bot/locales/messages.pot -d bot/locales -D messages

"""

from typing import Any
from aiogram.utils.i18n.middleware import I18nMiddleware
from bot.services.users import get_language_code

from aiogram.types import TelegramObject

from sqlalchemy.ext.asyncio import AsyncSession


class ACLMiddleware(I18nMiddleware):
    DEFAULT_LANGUAGE_CODE: str = "en"
    ALLOWED_LANGUAGE_CODES: list[str] = ["en", "ru", "uk"]

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:

        session: AsyncSession = data["session"]

        if not getattr(event, "from_user", None):
            return self.DEFAULT_LANGUAGE_CODE

        user_id = event.from_user.id
        language_code: str | None = await get_language_code(session=session, user_id=user_id)

        language_code = (
            language_code
            if language_code in self.ALLOWED_LANGUAGE_CODES
            else self.DEFAULT_LANGUAGE_CODE
        )

        return language_code
