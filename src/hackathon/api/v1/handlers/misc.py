from starlite import Router, get

from hackathon.config.settings import AppSettings, get_settings

settings = get_settings()


@get(settings.api.HEALTHCHECK_PATH, summary="Service health")
async def healthcheck() -> AppSettings:
    """Check service health."""
    return settings.app


router = Router(path="", tags=["Misc"], route_handlers=[healthcheck])
