from functools import partial

from starlite import Provide, Starlite
from starlite.plugins.sql_alchemy import SQLAlchemyPlugin

from hackathon.api.urls import api_router
from hackathon.config.settings import get_settings
from hackathon.infrastructure.db import redis
from hackathon.lib import compression, exceptions, logging, openapi, response, sqlalchemy_plugin, static_files

from .containers import Container, override_providers

settings = get_settings()

dependencies = {
    settings.api.CONFIG_DEPENDENCY_KEY: Provide(get_settings),
    settings.api.REDIS_CLIENT_DEPENDENCY_KEY: Provide(redis.get_redis_client),
}


async def on_startup(*_, container: Container, **__) -> None:
    """Startup hook."""
    await container.init_resources()
    container.check_dependencies()


async def on_shutdown(*_, container: Container, **__) -> None:
    """Shutdown hook."""
    await container.shutdown_resources()


def create_app() -> Starlite:
    """Starlite app factory."""
    container = Container()
    container.config.from_pydantic(settings=settings)
    container = override_providers(container)

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
        on_shutdown=[partial(on_shutdown, container=container)],
        on_startup=[partial(on_startup, container=container)],
        static_files_config=static_files.config,
    )
    return app
