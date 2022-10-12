import pytest

pytestmark = [pytest.mark.asyncio]


async def test_ok(client):
    """Endpoint /healthcheck returns 200 HTTP status."""
    response = await client.get("/api/v1/healthcheck")

    assert response["status"] == "ok"
