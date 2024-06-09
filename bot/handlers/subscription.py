from pathlib import Path
from typing import Literal, TypeAlias
from aiogram import F, Router
from aiogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramNotFound
from aiogram.utils.i18n import gettext as _
from aiogram.methods import GetChatMember
from bot.bot_controller import send_message, try_delete_message
from bot.services.users import get_language_code, set_twitter_username, set_youtube_screenshot
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession


router = Router()


TargetSubscriber: TypeAlias = Literal["everyone", "by_language_code"]
SubscribeValuesType: TypeAlias = dict[str | int, str]

telegram_chat_ids: dict[TargetSubscriber, SubscribeValuesType] = {
    "everyone": {},
    "by_language_code": {
        "ru": {
            -1002001545830: "gb1905 Telegram",
            # -1002129933465: "Telegram Channel",
            # -1002127860743: "Telegram Chat",
        },
        "en": {
            # -1002144265171: "Telegram Channel",
            # -1002127860743: "Telegram Chat",
        },
    },
}
twitter_usernames: dict[TargetSubscriber, SubscribeValuesType] = {
    "everyone": {
        "meetpay_crypto": "Twitter Page",
    },
}
youtube_usernames: dict[TargetSubscriber, SubscribeValuesType] = {
    "everyone": {
        "meetpay_crypto": "YouTube Channel",
    },
}


async def get_subscribe_values_for_user(
    subscribe_values: dict[TargetSubscriber, SubscribeValuesType],
    session: AsyncSession,
    user_id: int,
) -> SubscribeValuesType:
    values: dict[int, str] = {}

    for_everyone = subscribe_values.get("everyone")
    if for_everyone:
        for key, value in for_everyone.items():
            values[key] = value

    by_language_code = subscribe_values.get("by_language_code")
    if by_language_code:
        user_lang_code = await get_language_code(session, user_id)
        for language_code in by_language_code:
            if language_code == user_lang_code:
                for key, value in by_language_code[language_code].items():
                    values[key] = value

    return values


class States(StatesGroup):
    check_telegram_subscriptions = State("check_telegram_subscriptions")
    twitter_username = State("twitter_username")
    youtube_screenshot = State("youtube_screenshot")


async def send_telegram_subscriptions(
    session: AsyncSession,
    bot: Bot,
    user_id: int,
    state: FSMContext,
    retried: bool = False,
) -> None:
    if not retried:
        text = _("<b>Meet</b> and subscribe our official communities:")
    else:
        text = _("Looks like you haven’t subscribed to our communities. Please try again.")

    keyboard = []
    chats = await get_user_telegram_chats_to_subscribe(session, user_id)
    for chat_id, button_text in chats.items():
        url = await _export_chat_invite_link(chat_id=chat_id, bot=bot)
        keyboard.append([IKB(text=_(button_text), url=url)])

    keyboard.append([IKB(text=_("✅ Done"), callback_data="check_subscription")])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    tempdata = await state.get_data()
    await try_delete_message(bot, user_id, tempdata.get("ex_message_id"))
    msg = await send_message(
        bot=bot,
        chat_id=user_id,
        text=text,
        reply_markup=markup,
    )
    await state.set_state(States.check_telegram_subscriptions)
    await state.update_data({"ex_message_id": msg.message_id})


async def send_twitter_subscriptions(
    session: AsyncSession,
    bot: Bot,
    user_id: int,
    state: FSMContext,
) -> None:
    text = _(
        "Brilliant! The next step is to <b>meet</b> our Twitter Page"
        " and send your Twitter username (@username format) below:"
    )

    keyboard = []
    usernames = await get_user_twitter_usernames_to_follow(session, user_id)
    for username, button_text in usernames.items():
        keyboard.append([IKB(text=_(button_text), url=f"https://x.com/{username}")])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    tempdata = await state.get_data()
    await try_delete_message(bot, user_id, tempdata.get("ex_message_id"))
    msg = await send_message(
        bot=bot,
        chat_id=user_id,
        text=text,
        reply_markup=markup,
    )
    await state.set_state(States.twitter_username)
    await state.update_data({"ex_message_id": msg.message_id})


async def send_youtube_subscriptions(
    session: AsyncSession,
    bot: Bot,
    user_id: int,
    state: FSMContext,
) -> None:
    text = _("Spectacular, last step! <b>Meet</b> our Youtube, subscribe and provide a screenshot:")

    keyboard = []
    usernames = await get_user_youtube_usernames_to_follow(session, user_id)
    for username, button_text in usernames.items():
        keyboard.append([IKB(text=_(button_text), url=f"https://www.youtube.com/@{username}")])
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    tempdata = await state.get_data()
    await try_delete_message(bot, user_id, tempdata.get("ex_message_id"))
    msg = await send_message(
        bot=bot,
        chat_id=user_id,
        text=text,
        reply_markup=markup,
    )
    await state.set_state(States.youtube_screenshot)
    await state.update_data({"ex_message_id": msg.message_id})


@router.message(States.youtube_screenshot)
async def youtube_screenshot_handler(
    message: Message, session: AsyncSession, bot: Bot, state: FSMContext
):
    from .menu import send_menu

    await state.set_state()

    user = message.from_user

    if message.photo:
        file = await bot.get_file(message.photo[-1].file_id)
        file_bytes_io = await bot.download_file(file.file_path)
        filename = Path(file.file_path).stem
        save_to_path = Path(f"photos/{filename}.jpg")  # TODO: move path to var
        save_to_path.write_bytes(file_bytes_io.read())

        await set_youtube_screenshot(
            session=session, user_id=user.id, youtube_screenshot=str(filename)
        )
        return await send_menu(bot=bot, session=session, user_id=user.id, state=state)

    return await send_youtube_subscriptions(session=session, bot=bot, user_id=user.id, state=state)


@router.message(States.twitter_username, F.text.regexp(r"^@\w{1,15}$"))
async def twitter_username_handler(
    message: Message, session: AsyncSession, bot: Bot, state: FSMContext
):
    from .menu import send_menu

    await state.set_state()
    user = message.from_user
    twitter_username = message.text.strip("@")
    await set_twitter_username(session=session, user_id=user.id, twitter_username=twitter_username)
    return await send_menu(bot=bot, session=session, user_id=user.id, state=state)


@router.callback_query(F.data.regexp(r"check_subscription"), States.check_telegram_subscriptions)
async def check_telegram_subscription_on_query(
    query: CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext
):
    from .menu import send_menu

    await state.set_state()
    user = query.from_user

    if await is_subscribed_telegram_chats(session=session, bot=bot, user_id=user.id):
        return await send_menu(bot=bot, session=session, user_id=user.id, state=state)
    await send_telegram_subscriptions(
        session=session,
        user_id=user.id,
        bot=bot,
        state=state,
        retried=True,
    )


async def is_subscribed_telegram_chats(session: AsyncSession, bot: Bot, user_id: int) -> bool:
    if telegram_chat_ids:
        for chat_id in await get_user_telegram_chats_to_subscribe(session=session, user_id=user_id):
            if not await is_subscribed_to_chat(bot=bot, user_id=user_id, chat_id=chat_id):
                return False
    return True


async def is_subscribed_to_chat(bot: Bot, user_id: int, chat_id: int) -> bool:
    try:
        member = await bot(GetChatMember(chat_id=chat_id, user_id=user_id))
        assert member.status not in (
            ChatMemberStatus.LEFT,
            ChatMemberStatus.KICKED,
            ChatMemberStatus.RESTRICTED,
        )
    except (TelegramNotFound, AssertionError):
        return False
    return True


async def get_user_telegram_chats_to_subscribe(
    session: AsyncSession, user_id: int
) -> SubscribeValuesType:
    return await get_subscribe_values_for_user(telegram_chat_ids, session, user_id)


async def get_user_twitter_usernames_to_follow(
    session: AsyncSession, user_id: int
) -> SubscribeValuesType:
    return await get_subscribe_values_for_user(twitter_usernames, session, user_id)


async def get_user_youtube_usernames_to_follow(
    session: AsyncSession, user_id: int
) -> SubscribeValuesType:
    return await get_subscribe_values_for_user(youtube_usernames, session, user_id)


async def _export_chat_invite_link(bot: Bot, chat_id: int) -> str:
    return await bot.export_chat_invite_link(chat_id)
