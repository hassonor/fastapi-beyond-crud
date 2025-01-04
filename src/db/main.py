from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlmodel import create_engine, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Config

async_engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL,
        echo=True
    )
)


async def init_db():
    from src.books.models import Book  # noqa
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
