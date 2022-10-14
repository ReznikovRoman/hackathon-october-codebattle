from functools import partial

from starlite import Starlite, State
from starlite.plugins.sql_alchemy import SQLAlchemyPlugin

from hackathon.api.urls import api_router
from hackathon.config.settings import get_settings
from hackathon.lib import compression, exceptions, logging, openapi, response, sqlalchemy_plugin, static_files

from .containers import Container, override_providers
from .dependencies import create_dependencies

settings = get_settings()


async def on_startup(state: State, *_, container: Container, **__) -> None:
    """Startup hook."""
    await container.init_resources()
    container.check_dependencies()
    state.container = container


async def on_shutdown(state: State) -> None:
    """Shutdown hook."""
    await state.container.shutdown_resources()


def create_app() -> Starlite:
    """Starlite app factory."""
    container = Container()
    container.config.from_pydantic(settings=settings)
    container = override_providers(container)

    dependencies = create_dependencies()
    app = Starlite(
        after_exception=[exceptions.after_exception_hook_handler],
        compression_config=compression.config,
        debug=settings.app.DEBUG,
        dependencies=dependencies,
        exception_handlers={
            exceptions.HackathonAPIError: exceptions.project_api_exception_to_http_response,
            Exception: exceptions.server_exception_to_http_response,
        },
        logging_config=logging.config,
        openapi_config=openapi.config,
        response_class=response.Response,
        route_handlers=[api_router],
        plugins=[SQLAlchemyPlugin(config=sqlalchemy_plugin.config)],
        on_shutdown=[on_shutdown],
        on_startup=[partial(on_startup, container=container)],
        static_files_config=static_files.config,
    )
    app.state.container = container  # XXX: have to manually specify `container` for unit tests
    return app
