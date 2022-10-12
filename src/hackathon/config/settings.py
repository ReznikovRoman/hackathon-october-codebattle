from functools import lru_cache
from typing import Union

from pydantic import AnyHttpUrl, BaseSettings, Field, validator


class EnvConfig(BaseSettings.Config):

    @classmethod
    def prepare_field(cls, field) -> None:
        if "env_names" in field.field_info.extra:
            return
        return super().prepare_field(field)


class Settings(BaseSettings):
    """Project settings."""

    # Project
    API_V1_STR: str = Field("/api/v1")
    SERVER_NAME: str
    SERVER_HOSTS: Union[str, list[AnyHttpUrl]]
    PROJECT_NAME: str
    DEBUG: bool = Field(False)
    PROJECT_BASE_URL: str

    # Configuration
    USE_STUBS: bool = Field(False)

    class Config(EnvConfig):
        env_prefix = "HOC_"
        case_sensitive = True

    @validator("SERVER_HOSTS", pre=True)
    def _assemble_server_hosts(cls, server_hosts):
        if isinstance(server_hosts, str):
            return [item.strip() for item in server_hosts.split(",")]
        return server_hosts


@lru_cache()
def get_settings() -> "Settings":
    return Settings()
