import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.responses import Response

from starlite import MediaType, ValidationException
from starlite.connection import Request

from .schemas import BaseErrorResponse, ErrorResponse

if TYPE_CHECKING:
    from starlite.datastructures import State
    from starlite.types import Scope

logger = logging.getLogger(__name__)


class APIErrorMixin:
    """REST API error mixin."""

    message: str = "Server error"
    code: str = "server_error"
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str | None = None, code: str | None = None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> dict:
        dct = {
            "error": {
                "code": self.code,
                "message": self.message,
            },
        }
        return dct


class BaseHackathonError(Exception):
    """Base service error."""


class RepositoryError(BaseHackathonError):
    """Base repository exception type."""


class HackathonAPIError(APIErrorMixin, BaseHackathonError):
    """Hackathon service error."""


class NotFoundError(HackathonAPIError):
    """Resource is not found."""

    message = "Resource not found"
    code = "not_found"
    status_code = HTTPStatus.NOT_FOUND


class ConflictError(HackathonAPIError):
    """Resource conflict."""

    message = "Resource cannot be processed"
    code = "resource_conflict"
    status_code = HTTPStatus.CONFLICT


class ImproperlyConfiguredError(HackathonAPIError):
    """Improperly configured service."""

    message = "Improperly configured service"
    code = "improperly_configured"
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR


class AuthorizationError(HackathonAPIError):
    """Authorization error."""

    message = "Authorization error"
    code = "authorization_error"
    status_code = HTTPStatus.UNAUTHORIZED


class RequiredHeaderMissingError(HackathonAPIError):
    """Required header is missing in the request."""

    message = "Required header is missing"
    code = "missing_header"
    status_code = HTTPStatus.BAD_REQUEST


async def after_exception_hook_handler(exc: Exception, scope: "Scope", state: "State") -> None:
    """Logs exception and returns appropriate response.

    Args:
        exc: the exception that was raised.
        scope: scope of the request.
        state: application state.
    """
    logger.error(
        "Application Exception\n\nRequest Scope: %s\n\nApplication State: %s\n\n",
        scope,
        state.dict(),
        exc_info=exc,
    )
    if db_session := state.get("_sqlalchemy_repository_session", None):
        logging.exception("Session rollback because of exception.")
        await db_session.rollback()
        await db_session.close()


def _create_error_response_from_starlite_middleware(request: Request, exc: Exception) -> Response:
    server_middleware = ServerErrorMiddleware(app=request.app)
    return server_middleware.debug_response(request=request, exc=exc)


def starlite_validation_exception_to_http_response(_: Request, exc: ValidationException) -> Response:
    """Transform starlite validation exception to project specific HTTP exceptions.

    Args:
        _: The request that experienced the exception.
        exc: Exception raised during handling of the request.

    Returns: Exception response appropriate to the type of original exception.
    """
    content = BaseErrorResponse(error=ErrorResponse(message=exc.detail, code="validation_error", extra=exc.extra))
    return Response(
        media_type=MediaType.JSON, content=content.json(exclude_none=True), status_code=HTTPStatus.BAD_REQUEST)


def project_api_exception_to_http_response(request: Request, exc: HackathonAPIError) -> Response:
    """Transform project API exceptions to HTTP exceptions.

    Args:
        request: The request that experienced the exception.
        exc: Exception raised during handling of the request.

    Returns: Exception response appropriate to the type of original exception.
    """
    if exc is HackathonAPIError and request.app.debug:
        return _create_error_response_from_starlite_middleware(request, exc)
    content = BaseErrorResponse(error=ErrorResponse(message=exc.message, code=exc.code))
    return Response(media_type=MediaType.JSON, content=content.json(exclude_none=True), status_code=exc.status_code)


def server_exception_to_http_response(request: Request, exc: Exception) -> Response:
    """Transform unhandled server exceptions to HTTP exceptions.

    Args:
        request: The request that experienced the exception.
        exc: Exception raised during handling of the request.

    Returns: Exception response appropriate to the type of original exception.
    """
    if isinstance(exc, IntegrityError):
        raise ConflictError from exc
    elif isinstance(exc, SQLAlchemyError):
        raise RepositoryError(f"An exception occurred: {exc}") from exc
    if request.app.debug:
        return _create_error_response_from_starlite_middleware(request, exc)
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    content = BaseErrorResponse(error=ErrorResponse(message=str(exc)))
    return Response(media_type=MediaType.JSON, content=content.json(exclude_none=True), status_code=status_code)
