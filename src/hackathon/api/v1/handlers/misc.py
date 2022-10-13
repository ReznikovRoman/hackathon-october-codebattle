from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from starlite import Router, get

from hackathon.config.settings import AppSettings, get_settings

settings = get_settings()


@get(settings.api.HEALTHCHECK_PATH, summary="Service health", cache=False)
async def healthcheck(redis_client: Redis, db_session: AsyncSession) -> AppSettings:
    """Verifies that Postgres and Redis are available and returns app config info."""
    assert await redis_client.ping() is True
    assert (await db_session.execute(text("SELECT 1"))).scalar_one() == 1
    return settings.app


router = Router(path="", tags=["Misc"], route_handlers=[healthcheck])
