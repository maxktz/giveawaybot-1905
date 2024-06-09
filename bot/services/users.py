from aiogram import Bot
from loguru import logger
from sqlalchemy import func, select, text, update

from bot.cache.redis import cached, set_cache
from bot.cache.key_builder import KeyBuilder
from bot.database.models import UserModel

from aiogram.types import User
from sqlalchemy.ext.asyncio import AsyncSession


key_buider = KeyBuilder()


async def add_user(
    session: AsyncSession,
    user: User,
    referrer_id: int | None,
    bot: Bot,
) -> int | None:
    """Add a new user to the database.
    Returns inserted referrer_id"""
    if referrer_id is not None:
        try:
            referrer_id = int(referrer_id)
        except ValueError:
            referrer_id = None

    # Check that referrer is valid user
    user_referrer_id = None
    if referrer_id and referrer_id != user.id:
        if await is_valid_referrer(session, referrer_id):
            user_referrer_id = referrer_id

    user_id: int = user.id
    first_name: str = user.first_name
    last_name: str | None = user.last_name
    username: str | None = user.username
    language_code: str | None = None
    is_premium: bool = user.is_premium or False

    new_user = UserModel(
        id=user_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        language_code=language_code,
        is_premium=is_premium,
        referrer_id=user_referrer_id,
    )

    session.add(new_user)
    await session.commit()
    await set_cache(key=key_buider(user_id, func=user_exists), value=True)

    return user_referrer_id


@cached(build_key=lambda session, user_id: key_buider(user_id, func=user_exists))
async def user_exists(session: AsyncSession, user_id: int) -> bool:
    """Checks if the user is in the database."""
    query = select(UserModel.id).filter_by(id=user_id).limit(1)

    result = await session.execute(query)

    user = result.scalar_one_or_none()
    return bool(user)


@cached(build_key=lambda session, user_id: key_buider(user_id, func=get_user))
async def get_user(session: AsyncSession, user_id: int) -> UserModel:
    query = select(UserModel).filter_by(id=user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    return user


@cached(build_key=lambda session, user_id: key_buider(user_id, func=get_first_name))
async def get_first_name(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.first_name).filter_by(id=user_id)

    result = await session.execute(query)

    first_name = result.scalar_one_or_none()
    return first_name or ""


@cached(build_key=lambda session, user_id: key_buider(user_id, func=get_user_referrals_count))
async def get_user_referrals_count(session: AsyncSession, user_id: int) -> int:
    query = text(
        "SELECT COUNT(*) FROM users WHERE referrer_id = :user_id AND is_participant = True"
    )
    result = await session.execute(query, {"user_id": user_id})
    count = result.scalar()
    return count


@cached(build_key=lambda session, user_id: key_buider(user_id, func=get_twitter_username))
async def get_twitter_username(session: AsyncSession, user_id: int) -> str | None:
    query = select(UserModel.twitter_username).filter_by(id=user_id)

    result = await session.execute(query)

    twitter_username = result.scalar_one_or_none()
    return twitter_username


@cached(build_key=lambda session, user_id: key_buider(user_id, func=get_youtube_screenshot))
async def get_youtube_screenshot(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.youtube_screenshot).filter_by(id=user_id)
    result = await session.execute(query)
    youtube_screenshot = result.scalar_one_or_none()
    return youtube_screenshot


@cached(build_key=lambda session, user_id: key_buider(user_id, func=get_language_code))
async def get_language_code(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.language_code).filter_by(id=user_id)

    result = await session.execute(query)

    language_code = result.scalar_one_or_none()
    return language_code


@cached(build_key=lambda session, user_id: key_buider(user_id, func=get_is_admin))
async def get_is_admin(session: AsyncSession, user_id: int) -> bool:
    query = select(UserModel.is_admin).filter_by(id=user_id)

    result = await session.execute(query)

    is_admin = result.scalar_one_or_none()
    return bool(is_admin)


@cached(build_key=lambda session, user_id: key_buider(user_id, func=is_valid_referrer))
async def is_valid_referrer(session: AsyncSession, user_id: int) -> bool:
    query = select(
        UserModel.is_verified,
        UserModel.twitter_username,
        UserModel.youtube_screenshot,
    ).filter_by(id=user_id)

    result = await session.execute(query)
    selection = result.one_or_none()

    if selection is None:
        return False

    is_valid: bool = all(selection)
    return is_valid


@cached(build_key=lambda session, user_id: key_buider(user_id, func=get_is_verified))
async def get_is_verified(session: AsyncSession, user_id: int) -> bool:
    query = select(UserModel.is_verified).filter_by(id=user_id)
    result = await session.execute(query)
    return bool(result.scalar_one_or_none())


@cached(build_key=lambda session, user_id: key_buider(user_id, func=get_is_participant))
async def get_is_participant(session: AsyncSession, user_id: int) -> bool:
    query = select(UserModel.is_participant).filter_by(id=user_id)
    result = await session.execute(query)
    return bool(result.scalar_one_or_none())


@cached(build_key=lambda session: key_buider(func=get_all_users))
async def get_all_users(session: AsyncSession) -> list[UserModel]:
    query = select(UserModel)

    result = await session.execute(query)

    users = result.scalars()
    return list(users)


@cached(build_key=lambda session: key_buider(func=get_all_users))
async def get_user_count(session: AsyncSession) -> int:
    query = select(func.count()).select_from(UserModel)

    result = await session.execute(query)

    count = result.scalar_one_or_none() or 0
    return int(count)


@cached(build_key=lambda session, user_id: key_buider(user_id, func=get_user_referrer_id))
async def get_user_referrer_id(session: AsyncSession, user_id: int) -> int | None:
    query = select(UserModel.referrer_id).filter_by(id=user_id)
    result = await session.execute(query)
    referrer_id = result.scalar_one_or_none()
    return referrer_id


async def set_twitter_username(session: AsyncSession, user_id: int, twitter_username: str) -> None:
    stmt = (
        update(UserModel).where(UserModel.id == user_id).values(twitter_username=twitter_username)
    )

    await session.execute(stmt)
    await session.commit()

    await set_cache(key=key_buider(user_id, func=get_twitter_username), value=twitter_username)


async def set_youtube_screenshot(
    session: AsyncSession,
    user_id: int,
    youtube_screenshot: str,
) -> None:
    stmt = (
        update(UserModel)
        .where(UserModel.id == user_id)
        .values(youtube_screenshot=youtube_screenshot)
    )
    await session.execute(stmt)
    await session.commit()

    await set_cache(key=key_buider(user_id, func=get_youtube_screenshot), value=youtube_screenshot)


async def set_language_code(
    session: AsyncSession,
    user_id: int,
    language_code: str,
) -> None:
    stmt = update(UserModel).where(UserModel.id == user_id).values(language_code=language_code)

    await session.execute(stmt)
    await session.commit()

    await set_cache(key=key_buider(user_id, func=get_language_code), value=language_code)


async def set_is_verified(session: AsyncSession, user_id: int, is_verified: bool) -> None:
    stmt = update(UserModel).where(UserModel.id == user_id).values(is_verified=is_verified)
    await session.execute(stmt)
    await session.commit()

    await set_cache(key=key_buider(user_id, func=get_is_verified), value=is_verified)


async def set_is_admin(session: AsyncSession, user_id: int, is_admin: bool) -> None:
    stmt = update(UserModel).where(UserModel.id == user_id).values(is_admin=is_admin)
    await session.execute(stmt)
    await session.commit()
    await set_cache(key=key_buider(user_id, func=get_is_admin), value=is_admin)


async def set_is_participant(
    bot: Bot, session: AsyncSession, user_id: int, is_participant: bool
) -> None:
    from bot.handlers.referrals import (
        send_new_referral_notification,
        send_lost_referral_notification,
    )

    stmt = update(UserModel).where(UserModel.id == user_id).values(is_participant=is_participant)
    await session.execute(stmt)
    await session.commit()
    await set_cache(key=key_buider(user_id, func=get_is_participant), value=is_participant)

    referrer_id = await get_user_referrer_id(session, user_id)
    try:
        if referrer_id:
            if is_participant:
                notify_referrer = send_new_referral_notification
            else:
                notify_referrer = send_lost_referral_notification
            await notify_referrer(
                bot=bot,
                session=session,
                user_id=referrer_id,
                referral_id=user_id,
            )
    except Exception as e:
        logger.error(f"Cannot send notification about new referral - {e}")


def count_points_per_referrals(referrals: int) -> int:
    return 1


def count_all_points(referrals: int) -> int:
    return count_points_per_referrals(referrals) + 1
