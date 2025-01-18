# File: src/tests/fixtures/client_fixture.py

import pytest_asyncio
import httpx
from httpx import ASGITransport

from src import app  # The main FastAPI instance


@pytest_asyncio.fixture
async def async_client():
    """
    Provides an httpx.AsyncClient that is properly opened and closed,
    with an ASGITransport pointing to our FastAPI app,
    and a base_url of "http://testserver".
    """
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
