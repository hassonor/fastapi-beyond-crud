# File: src/tests/fixtures/client_fixture.py

import pytest
import httpx
from httpx import ASGITransport
from src import app  # your main FastAPI instance


@pytest.fixture
async def async_client():
    """
    Replaces httpx.AsyncClient(app=app, base_url=...)
    with the recommended transport=ASGITransport(app=...).
    Eliminates the "The 'app' shortcut is now deprecated" DeprecationWarning.
    """
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
