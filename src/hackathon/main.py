from starlite import Starlite

from hackathon.api.urls import api_router
from hackathon.config.settings import get_settings
from hackathon.lib import compression, logging, openapi, response, static_files

settings = get_settings()


def create_app() -> Starlite:
    """Starlite app factory."""
    app = Starlite(
        route_handlers=[api_router],
        response_class=response.Response,
        openapi_config=openapi.config,
        logging_config=logging.config,
        compression_config=compression.config,
        static_files_config=static_files.config,
    )
    return app
