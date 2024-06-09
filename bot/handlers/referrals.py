from aiogram import Bot
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.bot_controller import send_message
from bot.services.users import (
    count_points_per_referrals,
    get_user,
)


async def send_new_referral_notification(
    bot: Bot, session: AsyncSession, user_id: str, referral_id: int
) -> None:
    referral_user = await get_user(session, referral_id)

    point = count_points_per_referrals(1)
    name = f"@{referral_user.username}" if referral_user.username else referral_user.first_name

    text = _(
        "You have got a new referral! For {name} you got +{point} to your points",
        locale=referral_user.language_code,
    ).format(name=name, point=point)

    await send_message(bot=bot, chat_id=user_id, text=text)


async def send_lost_referral_notification(
    bot: Bot, session: AsyncSession, user_id: str, referral_id: int
) -> None:
    referral_user = await get_user(session, referral_id)

    point = count_points_per_referrals(1)
    name = f"@{referral_user.username}" if referral_user.username else referral_user.first_name

    text = _(
        "You have lost one of your referrals! {name} has left you and are not participating. -{point} points",
        locale=referral_user.language_code,
    ).format(name=name, point=point)

    await send_message(bot=bot, chat_id=user_id, text=text)
