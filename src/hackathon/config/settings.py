from functools import lru_cache
from typing import Final, Literal, Union

from pydantic import AnyHttpUrl, BaseSettings, Field, PostgresDsn, RedisDsn, validator


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

    @property
    def slug(self) -> str:
        """A slugified name.

        Returns: `self.PROJECT_NAME`, all lowercase and hyphens instead of spaces.
        """
        return "-".join(s.lower() for s in self.PROJECT_NAME.split())


class APISettings(BaseSettings):
    """API specific settings."""

    V1_STR: str = Field("/api/v1")
    HEALTHCHECK_PATH: str = Field("/healthcheck")

    DEFAULT_PAGINATION_LIMIT: int = Field(10)

    CONTAINER_DEPENDENCY_KEY: Final[str] = "container"
    CONFIG_DEPENDENCY_KEY: str = Field("config")
    REDIS_CLIENT_DEPENDENCY_KEY: str = Field("redis_client")
    DB_SESSION_DEPENDENCY_KEY: str = Field("db_session")

    class Config(EnvConfig):
        env_prefix = "HOC_API"
        case_sensitive = True


class DatabaseSettings(BaseSettings):
    """Database specific settings."""

    # Config
    ECHO: bool
    ECHO_POOL: bool | Literal["debug"]
    POOL_DISABLE: bool
    POOL_MAX_OVERFLOW: int
    POOL_SIZE: int
    POOL_TIMEOUT: int

    # Connection
    HOST: str
    PORT: int
    NAME: str
    USER: str
    PASSWORD: str
    URL: PostgresDsn | None = None

    class Config(EnvConfig):
        env_prefix = "HOC_DB_"
        case_sensitive = True

    @validator("URL", pre=True)
    def get_url(cls, value, values) -> str:
        if value is not None:
            return value
        user = values["USER"]
        password = values["PASSWORD"]
        host = values["HOST"]
        port = values["PORT"]
        database = values["NAME"]
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"


class RedisSettings(BaseSettings):
    """Redis specific settings."""

    # Config
    DEFAULT_CHARSET: str
    DECODE_RESPONSES: bool
    RETRY_ON_TIMEOUT: bool

    # Connection
    HOST: str
    PORT: int
    DB: int
    URL: RedisDsn | None = None

    class Config(EnvConfig):
        env_prefix = "HOC_REDIS_"
        case_sensitive = True

    @validator("URL", pre=True)
    def get_url(cls, value, values) -> str:
        if value is not None:
            return value
        host = values["HOST"]
        port = values["PORT"]
        database = values["DB"]
        return f"redis://{host}:{port}/{database}"


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
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    openapi: OpenAPISettings = OpenAPISettings()
    server: ServerSettings = ServerSettings()

    # Configuration
    USE_STUBS: bool = Field(False)

    class Config(EnvConfig):
        env_prefix = "HOC_"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached `Settings` object."""
    return Settings()
