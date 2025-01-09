import pytest
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker


@pytest.fixture(scope="session")
def test_db_url():
    """
    Returns an in-memory SQLite for speed.
    For real usage, you might use a separate container DB for tests.
    """
    return "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
async def test_db_engine(test_db_url) -> AsyncEngine:
    """
    Creates an async engine for the test DB. Runs migrations or table creation if needed.
    """
    engine = create_engine(
        test_db_url,
        echo=False,
        connect_args={"check_same_thread": False},
        future=True
    )
    async_engine = AsyncEngine(engine)

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield async_engine
    await async_engine.dispose()


@pytest.fixture
async def db_session(test_db_engine) -> AsyncSession:
    """
    Yields an AsyncSession for each test, connected to the test DB engine.
    """
    session_factory = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
