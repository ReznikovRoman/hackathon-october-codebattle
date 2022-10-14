from typing import AsyncIterator

import redis.asyncio as aioredis

from hackathon.config.settings import RedisSettings


async def init_redis(config: RedisSettings) -> AsyncIterator[aioredis.Redis]:
    """Init async Redis client."""
    redis_client: aioredis.Redis = await aioredis.from_url(
        url=config.URL,
        decode_responses=config.DECODE_RESPONSES,
        retry_on_timeout=config.RETRY_ON_TIMEOUT,
    )
    yield redis_client
    await redis_client.close()
