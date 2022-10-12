from starlite import Starlite

from hackathon.api.urls import api_router
from hackathon.config.settings import get_settings

settings = get_settings()


def create_app() -> Starlite:
    """Starlite app factory."""
    app = Starlite(route_handlers=[api_router])
    return app
