from typing import Awaitable, Any, Callable

from datetime import timedelta
from functools import wraps
from core.loader import redis_client
from cache.serialization import PickleSerializer, AbstractSerializer


from redis.asyncio import Redis


CACHE_TTL_SECONDS = 300


def build_key(*args) -> str:
    args_str = ":".join(map(str, args))
    return f"{args_str}"


async def set_redis_value(
    key: bytes | str,
    value: bytes | str,
    ttl: int | timedelta | None = CACHE_TTL_SECONDS,
) -> None:
    if ttl:
        if isinstance(ttl, timedelta):
            ttl = int(ttl.total_seconds())
        await redis_client.set(key, value, ex=ttl)
    else:
        await redis_client.set(key, value)


def cached(
        ttl: int | timedelta | None = CACHE_TTL_SECONDS,
        key_builder: Callable = build_key,
        cache: Redis = redis_client,
        serializer: AbstractSerializer | None = None,
):
    if serializer is None:
        serializer = PickleSerializer()

    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            key = key_builder(*args, **kwargs)
            key = f"{func.__name__}:{key}"
            cached_value  = await cache.get(key)
            if cached_value  is not None:
                return serializer.deserialize(cached_value)
            result  = await func(*args, **kwargs)
            await set_redis_value(
                key=key,
                value=serializer.serialize(result),
                ttl=ttl,
            )
            return result
        return wrapper
    return decorator
