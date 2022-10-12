from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

import orjson
from httpx import AsyncClient

if TYPE_CHECKING:
    from httpx import Response

    APIResponse = Union[dict, str, list[dict], dict[str, Any]]


class APIClient(AsyncClient):
    """Httpx test client."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self, *args, **kwargs) -> APIResponse:
        return await self._api_call("get", kwargs.get("expected_status_code", 200), *args, **kwargs)

    async def post(self, *args, **kwargs) -> APIResponse:
        return await self._api_call("post", kwargs.get("expected_status_code", 201), *args, **kwargs)

    async def put(self, *args, **kwargs) -> APIResponse:
        return await self._api_call("put", kwargs.get("expected_status_code", 200), *args, **kwargs)

    async def patch(self, *args, **kwargs) -> APIResponse:
        return await self._api_call("patch", kwargs.get("expected_status_code", 200), *args, **kwargs)

    async def delete(self, *args, **kwargs) -> APIResponse:
        return await self._api_call("delete", kwargs.get("expected_status_code", 204), *args, **kwargs)

    async def _api_call(self, method: str, expected: int, *args, **kwargs) -> APIResponse:
        kwargs.pop("expected_status_code", None)
        as_response = kwargs.pop("as_response", False)

        method = getattr(super(), method)
        response = await method(*args, **kwargs)
        if as_response:
            return response

        content = self._decode(response)

        error_message = f"Got {response.status_code} instead of {expected}. Content is '{content}'"
        assert response.status_code == expected, error_message

        return content

    def _decode(self, response: Response) -> APIResponse:
        content = response.content.decode("utf-8", errors="ignore")
        if self.is_json(response):
            return orjson.loads(content)
        return content

    @staticmethod
    def is_json(response: Response) -> bool:
        content_type = response.headers.get("content-type", None)
        if content_type is None:
            return False
        return "json" in content_type
