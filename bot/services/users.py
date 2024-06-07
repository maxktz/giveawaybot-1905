from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import func, select, text, update

from bot.cache.redis import build_key, cached, clear_cache
from bot.database.models import UserModel

if TYPE_CHECKING:
    from aiogram.types import User
    from sqlalchemy.ext.asyncio import AsyncSession


async def add_user(
    session: AsyncSession,
    user: User,
    referrer_id: int | None,
) -> int | None:
    """Add a new user to the database.
    Returns inserted referrer_id"""
    if referrer_id is not None:
        try:
            referrer_id = int(referrer_id)
        except ValueError:
            referrer_id = None

    # Check that referrer is real user
    user_referrer_id = None
    if referrer_id and referrer_id != user.id:
        if await user_exists(session, referrer_id):  # TODO: check if referrer not is_blocked also
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
    await clear_cache(user_exists, user_id)
    return user_referrer_id


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def user_exists(session: AsyncSession, user_id: int) -> bool:
    """Checks if the user is in the database."""
    query = select(UserModel.id).filter_by(id=user_id).limit(1)

    result = await session.execute(query)

    user = result.scalar_one_or_none()
    return bool(user)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_first_name(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.first_name).filter_by(id=user_id)

    result = await session.execute(query)

    first_name = result.scalar_one_or_none()
    return first_name or ""


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_user_referrals_count(session: AsyncSession, user_id: int) -> int:
    query = text("SELECT COUNT(*) FROM users WHERE referrer_id = :user_id")
    result = await session.execute(query, {"user_id": user_id})
    count = result.scalar()
    return count


# @cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_twitter_username(session: AsyncSession, user_id: int) -> str | None:
    query = select(UserModel.twitter_username).filter_by(id=user_id)

    result = await session.execute(query)

    twitter_username = result.scalar_one_or_none()
    return twitter_username


async def set_twitter_username(session: AsyncSession, user_id: int, twitter_username: str) -> None:
    stmt = (
        update(UserModel).where(UserModel.id == user_id).values(twitter_username=twitter_username)
    )
    await session.execute(stmt)
    await session.commit()


# @cached(key_builder=lambda session, user_id: build_key(user_id))
async def get_youtube_screenshot(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.youtube_screenshot).filter_by(id=user_id)
    result = await session.execute(query)
    youtube_screenshot = result.scalar_one_or_none()
    return youtube_screenshot


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


async def get_language_code(session: AsyncSession, user_id: int) -> str:
    query = select(UserModel.language_code).filter_by(id=user_id)

    result = await session.execute(query)

    language_code = result.scalar_one_or_none()
    return language_code


async def set_language_code(
    session: AsyncSession,
    user_id: int,
    language_code: str,
) -> None:
    stmt = update(UserModel).where(UserModel.id == user_id).values(language_code=language_code)

    await session.execute(stmt)
    await session.commit()


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def is_admin(session: AsyncSession, user_id: int) -> bool:
    query = select(UserModel.is_admin).filter_by(id=user_id)

    result = await session.execute(query)

    is_admin = result.scalar_one_or_none()
    return bool(is_admin)


@cached(key_builder=lambda session, user_id: build_key(user_id))
async def is_verified(session: AsyncSession, user_id: int) -> bool:
    query = select(UserModel.is_verified).filter_by(id=user_id)
    result = await session.execute(query)
    return bool(result.scalar_one_or_none())


async def set_is_verified(session: AsyncSession, user_id: int, is_verified: bool) -> None:
    stmt = update(UserModel).where(UserModel.id == user_id).values(is_verified=is_verified)
    await session.execute(stmt)
    await session.commit()


async def set_is_admin(session: AsyncSession, user_id: int, is_admin: bool) -> None:
    stmt = update(UserModel).where(UserModel.id == user_id).values(is_admin=is_admin)

    await session.execute(stmt)
    await session.commit()


@cached(key_builder=lambda session: build_key())
async def get_all_users(session: AsyncSession) -> list[UserModel]:
    query = select(UserModel)

    result = await session.execute(query)

    users = result.scalars()
    return list(users)


@cached(key_builder=lambda session: build_key())
async def get_user_count(session: AsyncSession) -> int:
    query = select(func.count()).select_from(UserModel)

    result = await session.execute(query)

    count = result.scalar_one_or_none() or 0
    return int(count)
