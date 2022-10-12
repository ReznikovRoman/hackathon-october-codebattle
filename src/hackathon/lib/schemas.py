from orjson import orjson
from pydantic import BaseModel
from pydantic.generics import GenericModel


def orjson_dumps(value, *, default):
    return orjson.dumps(value, default=default).decode()


class BaseOrjsonSchema(BaseModel):
    """Base Pydantic orjson schema."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class ErrorResponse(BaseOrjsonSchema):
    """Error response content."""

    message: str = "Server error"
    code: str = "server_error"


class BaseErrorResponse(GenericModel):
    """Exception response schema."""

    error: ErrorResponse
