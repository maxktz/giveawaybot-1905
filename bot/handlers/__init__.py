from aiogram import Router


def get_handlers_router() -> Router:
    from . import export_users, menu, start, captcha, subscription, language

    router = Router()
    router.include_router(start.router)
    router.include_router(menu.router)
    router.include_router(export_users.router)
    router.include_router(captcha.router)
    router.include_router(subscription.router)
    router.include_router(language.router)

    return router
