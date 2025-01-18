# File: src/tests/fixtures/db_fixture.py

import pytest
import pytest_asyncio
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker


@pytest.fixture(scope="session")
def test_db_url():
    """
    Returns an in-memory SQLite for speed or any other test DB URL.
    """
    return "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_db_engine(test_db_url) -> AsyncEngine:
    """
    Creates an async engine for the test DB. Then do table creation if needed.
    """
    engine = create_engine(
        test_db_url,
        echo=False,
        connect_args={"check_same_thread": False},
        future=True
    )
    async_engine = AsyncEngine(engine)

    async with async_engine.begin() as conn:
        # Import all your SQLModel classes, then create
        await conn.run_sync(SQLModel.metadata.create_all)

    yield async_engine
    await async_engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_db_engine: AsyncEngine) -> AsyncSession:
    """
    Yields an actual AsyncSession for each test.
    """
    session_factory = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
