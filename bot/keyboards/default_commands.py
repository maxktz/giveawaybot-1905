from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

users_commands: dict[str, dict[str, str]] = {
    "en": {
        "menu": "Main menu",
        "language": "Сменить язык",
    },
    "ru": {
        "menu": "Главное меню",
        "language": "Сменить язык",
    },
}

admins_commands: dict[str, dict[str, str]] = {
    **users_commands,
    "en": {},
    "ru": {},
}


async def set_default_commands(bot: Bot) -> None:
    await remove_default_commands(bot)

    for language_code in users_commands:
        await bot.set_my_commands(
            [
                BotCommand(command=command, description=description)
                for command, description in users_commands[language_code].items()
            ],
            scope=BotCommandScopeDefault(),
        )

        """ Commands for admins
        for admin_id in await admin_ids():
            await bot.set_my_commands(
                [
                    BotCommand(command=command, description=description)
                    for command, description in admins_commands[language_code].items()
                ],
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        """


async def remove_default_commands(bot: Bot) -> None:
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
