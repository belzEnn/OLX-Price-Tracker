import redis.asyncio as aioredis
from os import getenv

REDIS_URL = getenv("REDIS_URL", "redis://localhost:6379")

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


async def is_seen(chat_id: int, query: str, listing_id: int) -> bool:
    r = await get_redis()
    return await r.sismember(f"seen:{chat_id}:{query}", listing_id)


async def mark_seen(chat_id: int, query: str, listing_id: int) -> None:
    r = await get_redis()
    await r.sadd(f"seen:{chat_id}:{query}", listing_id)
