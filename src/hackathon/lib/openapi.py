from pydantic_openapi_schema.v3_1_0 import Contact, Server

from starlite import OpenAPIConfig, OpenAPIController

from hackathon.config.settings import get_settings

settings = get_settings()


class CustomOpenAPIController(OpenAPIController):
    """OpenAPI controller with custom path."""

    path = f"{settings.api.V1_STR}/docs"


config = OpenAPIConfig(
    openapi_controller=CustomOpenAPIController,
    title=settings.openapi.TITLE or settings.app.PROJECT_NAME,
    version=settings.openapi.VERSION,
    contact=Contact(name=settings.openapi.CONTACT_NAME, email=settings.openapi.CONTACT_EMAIL),
    use_handler_docstrings=True,
    root_schema_site="swagger",
    servers=[Server(url=server) for server in settings.server.HOSTS],
)
