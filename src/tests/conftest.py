# src/tests/conftest.py

import os
import pytest
import pytest_asyncio
import httpx
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from unittest.mock import patch, AsyncMock
from httpx import ASGITransport

from src import app
from .mocks.redis_mock import AsyncRedisMock
from src.db.redis import token_blocklist_client

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"  # Force SQLite for tests


@pytest.fixture(scope="session")
def test_db_url():
    return "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_db_url):
    engine = create_engine(test_db_url, echo=False, future=True)
    async_engine = AsyncEngine(engine)
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield async_engine
    await async_engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def override_get_session(db_session):
    from src.db.main import get_session
    def _override():
        yield db_session

    app.dependency_overrides[get_session] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis globally."""
    redis_mock = AsyncRedisMock()
    with patch('src.db.redis.token_blocklist_client.redis', redis_mock), \
            patch('redis.asyncio.Redis', return_value=redis_mock), \
            patch('src.db.redis.redis.Redis', return_value=redis_mock):
        token_blocklist_client.redis = redis_mock
        yield redis_mock


@pytest.fixture(autouse=True)
def mock_mail():
    """Mock email functionality globally."""
    mail_mock = AsyncMock()
    mail_mock.send_message = AsyncMock(return_value=True)
    with patch('src.mail.mail', mail_mock), \
            patch('fastapi_mail.FastMail.send_message', mail_mock.send_message):
        yield mail_mock


@pytest.fixture(autouse=True)
def run_celery_inline():
    """
    Patch Celery so that calling `send_email_task.delay(...)` actually runs
    `send_email_task.run(...)` inline, letting `mail.send_message(...)` happen.
    """
    from src.celery_tasks import send_email_task

    def inline_run(*args, **kwargs):
        # This directly calls the Celery task's `run()` method,
        # so the body of the task is executed in the test.
        return send_email_task.run(*args, **kwargs)

    with patch('src.auth.routes.send_email_task.delay', side_effect=inline_run) as mock_task:
        yield mock_task


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
