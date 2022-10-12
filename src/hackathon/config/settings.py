from functools import lru_cache
from typing import Union

from pydantic import AnyHttpUrl, BaseSettings, Field, validator


class EnvConfig(BaseSettings.Config):
    """Settings environment config."""

    @classmethod
    def prepare_field(cls, field) -> None:
        if "env_names" in field.field_info.extra:
            return
        return super().prepare_field(field)


class AppSettings(BaseSettings):
    """Generic application settings."""

    BUILD_NUMBER: str
    DEBUG: bool = Field(False)
    ENVIRONMENT: str = Field("prod")
    LOG_LEVEL: str = Field("INFO")
    PROJECT_NAME: str
    PROJECT_BASE_URL: str

    class Config(EnvConfig):
        env_prefix = "HOC_"
        case_sensitive = True


class APISettings(BaseSettings):
    """API specific settings."""

    V1_STR: str = Field("/api/v1")
    HEALTHCHECK_PATH: str = Field("/healthcheck")

    class Config(EnvConfig):
        env_prefix = "HOC_API"
        case_sensitive = True


class OpenAPISettings(BaseSettings):
    """OpenAPI specific settings."""

    TITLE: str | None
    VERSION: str
    CONTACT_NAME: str
    CONTACT_EMAIL: str

    class Config(EnvConfig):
        env_prefix = "HOC_OPENAPI_"
        case_sensitive = True


class ServerSettings(BaseSettings):
    """Server specific settings."""

    PORT: int
    NAME: str
    HOSTS: Union[str, list[AnyHttpUrl]]

    class Config(EnvConfig):
        env_prefix = "HOC_SERVER_"
        case_sensitive = True

    @validator("HOSTS", pre=True)
    def _assemble_hosts(cls, hosts):
        if isinstance(hosts, str):
            return [item.strip() for item in hosts.split(",")]
        return hosts


class Settings(BaseSettings):
    """Project settings."""

    app: AppSettings = AppSettings()
    api: APISettings = APISettings()
    openapi: OpenAPISettings = OpenAPISettings()
    server: ServerSettings = ServerSettings()

    # Configuration
    USE_STUBS: bool = Field(False)

    class Config(EnvConfig):
        env_prefix = "HOC_"
        case_sensitive = True


@lru_cache()
def get_settings() -> "Settings":
    """Get cached `Settings` object."""
    return Settings()
