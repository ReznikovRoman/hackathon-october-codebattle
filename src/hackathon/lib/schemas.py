import uuid
from typing import TypeVar

from orjson import orjson
from pydantic import BaseModel
from pydantic.generics import GenericModel

SchemaT = TypeVar("SchemaT", bound="OrjsonSchema")


def orjson_dumps(value, *, default):
    return orjson.dumps(value, default=default).decode()


class BaseOrjsonSchema(BaseModel):
    """Base Pydantic orjson schema."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class OrjsonSchema(BaseModel):
    """Base for all Pydantic models."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        extra = "ignore"
        arbitrary_types_allowed = True
        orm_mode = True


class Schema(OrjsonSchema):
    """Base Pydantic Schema with ID."""

    id: uuid.UUID  # noqa: VNE003


class ErrorResponse(BaseOrjsonSchema):
    """Error response content."""

    message: str = "Server error"
    code: str = "server_error"


class BaseErrorResponse(GenericModel):
    """Exception response schema."""

    error: ErrorResponse
