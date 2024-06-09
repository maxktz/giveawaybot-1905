from aiogram import F, Router, types, Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from bot.bot_controller import send_message, try_delete_message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.subscription import (
    send_telegram_subscriptions,
    send_youtube_subscriptions,
)
from bot.services.users import (
    get_is_participant,
    get_language_code,
    get_twitter_username,
    get_user_referrals_count,
    get_youtube_screenshot,
    get_is_verified,
    set_is_participant,
)


router = Router(name="menu")


@router.message(F.text.regexp(r"^/menu$"))
async def menu_on_command(
    message: types.Message, session: AsyncSession, bot: Bot, state: FSMContext
) -> None:
    await state.set_state()
    await send_menu(user_id=message.from_user.id, session=session, bot=bot, state=state)


@router.callback_query(F.data.regexp(r"^menu$"))
async def menu_on_query(
    query: types.CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext
) -> None:
    await state.set_state()
    await send_menu(user_id=query.from_user.id, session=session, bot=bot, state=state)


async def send_menu(bot: Bot, session: AsyncSession, user_id: str, state: FSMContext) -> None:
    from .language import send_language
    from .captcha import send_captcha
    from .subscription import is_subscribed_telegram_chats, send_twitter_subscriptions

    locale = await get_language_code(session, user_id)
    if not locale:
        await send_language(bot, user_id, state)
        return

    is_participant = await get_is_participant(session, user_id)

    if not is_participant:
        if not await get_is_verified(session, user_id):
            await send_captcha(bot=bot, user_id=user_id, session=session, state=state)
            return

    if not await is_subscribed_telegram_chats(session, bot, user_id):
        if is_participant:
            await set_is_participant(bot, session, user_id, False)
        await send_telegram_subscriptions(session=session, bot=bot, user_id=user_id, state=state)
        return

    if not is_participant:

        if not await get_twitter_username(session, user_id):
            await send_twitter_subscriptions(session=session, bot=bot, user_id=user_id, state=state)
            return

        if not await get_youtube_screenshot(session, user_id):
            return await send_youtube_subscriptions(
                session=session, bot=bot, user_id=user_id, state=state
            )

        await set_is_participant(bot, session, user_id, True)

    tempdata = await state.get_data()

    referrals_count = await get_user_referrals_count(session, user_id)
    points = referrals_count + 1

    bot_username = (await bot.me()).username
    text = _(
        "Good job! Now you’re participating in our giveaway. \n"
        "\n"
        "Points: {points}. \n"
        "\n"
        "Invite friends to get more points: \n"
        "\n"
        "Invite link: {invite_link}",
        locale=locale,
    ).format(
        points=points,
        invite_link=f"t.me/{bot_username}?start={user_id}",
    )

    keyboard = [
        [InlineKeyboardButton(text=_("🔄 Update"), callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await try_delete_message(bot, user_id, tempdata.get("ex_message_id"))
    msg = await send_message(bot=bot, chat_id=user_id, text=text, reply_markup=markup)
    await state.update_data({"ex_message_id": msg.message_id})
