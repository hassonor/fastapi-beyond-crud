# File: src/tests/fixtures/client_fixture.py

import pytest
import httpx
from src import app  # Ensure src/__init__.py has app = FastAPI()


@pytest.fixture
def anyio_backend():
    """
    Required by httpx/pytest-asyncio if using anyio concurrency.
    """
    return "asyncio"


@pytest.fixture
async def async_client():
    """
    Provides an httpx.AsyncClient for integration tests against 'app'.
    """
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
