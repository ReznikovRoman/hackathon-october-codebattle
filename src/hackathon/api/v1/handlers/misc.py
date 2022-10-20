import contextlib
from typing import Annotated

from redis.asyncio import Redis

from starlite import Router, ServiceUnavailableException, get

from hackathon.config.settings import AppSettings, get_settings
from hackathon.containers import Container
from hackathon.lib.dependency_injector.ext.starlite import ProvideDI, inject
from hackathon.lib.repositories.sqlalchemy import SQLAlchemyRepository
from hackathon.lib.repositories.types import SessionFactory

settings = get_settings()


class HealthCheckFailure(ServiceUnavailableException):
    """Raise for health check failure."""


@get(settings.api.HEALTHCHECK_PATH, summary="Service health", cache=False)
@inject
async def healthcheck(
    session_factory: Annotated[SessionFactory, ProvideDI] = ProvideDI[Container.db.provided.session],
    redis_client: Annotated[Redis, ProvideDI] = ProvideDI[Container.redis_connection],
) -> AppSettings:
    """Verifies that Postgres and Redis are available and returns app config info."""
    with contextlib.suppress(Exception):
        if (
            await SQLAlchemyRepository.check_health(session_factory) and
            await redis_client.ping()
        ):
            return settings.app
    raise HealthCheckFailure("Databases are not ready.")


router = Router(path="", tags=["Misc"], route_handlers=[healthcheck])
