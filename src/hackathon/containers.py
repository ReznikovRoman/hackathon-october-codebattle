from dependency_injector import containers, providers

from hackathon.config.settings import get_settings
from hackathon.infrastructure.db import redis

__all__ = ["Container", "override_providers"]

settings = get_settings()


class Container(containers.DeclarativeContainer):
    """DI container."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "hackathon.api.v1.handlers.misc",
        ],
    )

    config = providers.Configuration()

    # Infrastructure

    redis_connection = providers.Resource(
        redis.init_redis,
        config=settings.redis,
    )


def override_providers(container: Container, /) -> Container:
    """Override providers with stubs."""
    if not container.config.USE_STUBS():
        return container
    return container


async def dummy_resource() -> None:
    """Dummy async resource for overriding providers in a DI container."""
