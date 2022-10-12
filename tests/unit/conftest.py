from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from hackathon.main import create_app

from .testlib import APIClient

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop


pytestmark = [pytest.mark.asyncio]


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def client() -> APIClient:
    async with APIClient(app=create_app(), base_url="http://test") as api_client:
        yield api_client
