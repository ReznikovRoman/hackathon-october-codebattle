from starlite import Starlite

from hackathon.api.urls import api_router
from hackathon.config.settings import get_settings
from hackathon.lib import compression, exceptions, logging, openapi, response, static_files

settings = get_settings()


def create_app() -> Starlite:
    """Starlite app factory."""
    app = Starlite(
        route_handlers=[api_router],
        debug=settings.app.DEBUG,
        exception_handlers={
            exceptions.HackathonAPIError: exceptions.project_api_exception_to_http_response,
            Exception: exceptions.server_exception_to_http_response,
        },
        after_exception=[exceptions.after_exception_hook_handler],
        response_class=response.Response,
        openapi_config=openapi.config,
        logging_config=logging.config,
        compression_config=compression.config,
        static_files_config=static_files.config,
    )
    return app
