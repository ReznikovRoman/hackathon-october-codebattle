from redis import asyncio as aioredis

from starlite import Provide, State

from hackathon.config.settings import get_settings

settings = get_settings()


async def get_redis_client(state: State) -> aioredis.Redis:
    """Dependency for retrieving a Redis client."""
    return await state.container.redis_connection()


def create_dependencies() -> dict[str, Provide]:
    """Create project dependencies."""
    dependencies = {
        settings.api.CONFIG_DEPENDENCY_KEY: Provide(get_settings),
        settings.api.REDIS_CLIENT_DEPENDENCY_KEY: Provide(get_redis_client),
    }
    return dependencies
