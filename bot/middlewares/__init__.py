from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from bot.core.loader import i18n as _i18n


def register_middlewares(dp: Dispatcher) -> None:
    from .auth import AuthMiddleware
    from .database import DatabaseMiddleware
    from .i18n import ACLMiddleware
    from .logging import LoggingMiddleware
    from .throttling import ThrottlingMiddleware

    dp.message.outer_middleware(ThrottlingMiddleware())

    dp.update.outer_middleware(LoggingMiddleware())

    dp.update.outer_middleware(DatabaseMiddleware())

    dp.message.middleware(ACLMiddleware(i18n=_i18n))
    dp.callback_query.middleware(ACLMiddleware(i18n=_i18n))
    dp.inline_query.middleware(ACLMiddleware(i18n=_i18n))
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    dp.message.middleware(AuthMiddleware())

    # subscribe_middleware = SubscribeMiddleware(
    #     telegram_chat_ids={
    #         -1002001545830: "gb1905 Telegram",
    #         "ru": {
    #             -1002129933465: "MEETPAY RU",
    #             -1002127860743: "MEETPAY CHAT RU",
    #         },
    #         "en": {
    #             -1002144265171: "MEETPAY NEWS EN",
    #             -1002127860743: "MEETPAY CHAT EN",
    #         },
    #     },
    #     twitter_usernames={
    #         "meetpay_crypto": "Twitter Page",
    #     },
    # )
    # dp.message.middleware(subscribe_middleware)
    # dp.include_router(subscribe_middleware.router)
