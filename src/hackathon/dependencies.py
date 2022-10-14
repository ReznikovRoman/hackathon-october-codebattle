from typing import TypeAlias

from dependency_injector.containers import DynamicContainer
from redis import asyncio as aioredis

from starlite import Provide

from hackathon.config.settings import get_settings
from hackathon.containers import Container

ContainerT: TypeAlias = Container | DynamicContainer

settings = get_settings()


async def get_redis_client(container: ContainerT) -> aioredis.Redis:
    """Dependency for retrieving a Redis client."""
    return await container.redis_connection()


def create_dependencies() -> dict[str, Provide]:
    """Create project dependencies."""
    dependencies = {
        settings.api.CONFIG_DEPENDENCY_KEY: Provide(get_settings),
        settings.api.REDIS_CLIENT_DEPENDENCY_KEY: Provide(get_redis_client),
    }
    return dependencies
