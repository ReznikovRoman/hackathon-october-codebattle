import contextlib

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from starlite import Router, ServiceUnavailableException, get

from hackathon.config.settings import AppSettings, get_settings
from hackathon.lib.repositories.sqlalchemy import SQLAlchemyRepository

settings = get_settings()


class HealthCheckFailure(ServiceUnavailableException):
    """Raise for health check failure."""


@get(settings.api.HEALTHCHECK_PATH, summary="Service health", cache=False)
async def healthcheck(redis_client: Redis, db_session: AsyncSession) -> AppSettings:
    """Verifies that Postgres and Redis are available and returns app config info."""
    with contextlib.suppress(Exception):
        if (
            await SQLAlchemyRepository.check_health(db_session) and
            await redis_client.ping()
        ):
            return settings.app
    raise HealthCheckFailure("Databases are not ready.")


router = Router(path="", tags=["Misc"], route_handlers=[healthcheck])
