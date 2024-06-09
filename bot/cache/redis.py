from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Optional

from redis.asyncio import Redis

from bot.core.loader import redis_client

from .base import DEFAULT_TTL
from .key_builder import KeyBuilder
from .serialization import AbstractSerializer, PickleSerializer


def cached(
    ttl: int | timedelta = DEFAULT_TTL,
    cache: Redis = redis_client,
    build_key: Optional[Callable[..., str]] = None,
    serializer: AbstractSerializer = PickleSerializer(),
) -> Callable:
    """Caches the functions return value into a key generated with module_name, function_name and args."""

    def decorator(func: Callable) -> Callable:

        if build_key is None:
            build_key_call = KeyBuilder(func=func)
        else:
            build_key_call = build_key

        @wraps(func)
        async def wrapper(*args: tuple[str, Any], **kwargs: dict[str, Any]) -> Any:
            key = build_key_call(*args, **kwargs)

            # Check if the key is in the cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                return serializer.deserialize(cached_value)

            # If not in cache, call the original function
            result = await func(*args, **kwargs)

            # Store the result in Redis
            await set_cache(
                key=key,
                value=result,
                ttl=ttl,
                serializer=serializer,
            )

            return result

        return wrapper

    return decorator


async def set_cache(
    key: str,
    value: Any,
    ttl: int | timedelta = DEFAULT_TTL,
    serializer: AbstractSerializer = PickleSerializer,
) -> None:
    value = serializer.serialize(value)
    await redis_client.set(key, value, ex=ttl)


async def clear_cache(key: str) -> None:
    await redis_client.delete(key)
