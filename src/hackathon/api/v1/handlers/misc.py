from starlite import Router, get


@get("/healthcheck", summary="Service health", description="Check service health.")
async def healthcheck() -> dict:
    """Check service health."""
    return {"status": "ok"}


router = Router(path="", tags=["Misc"], route_handlers=[healthcheck])
