from typing import Any

from asyncpg.pgproto import pgproto

import starlite


class Response(starlite.response.Response):
    """Custom `Response` that handles serialization of the postgres UUID type used by SQLAlchemy."""

    @staticmethod
    def serializer(value: Any) -> Any:
        """Serializes `value`.

        Args:
            value: The thing to be serialized.

        Returns:
            Serialized representation of `value`.
        """
        if isinstance(value, pgproto.UUID):
            return str(value)
        return starlite.Response.serializer(value)
