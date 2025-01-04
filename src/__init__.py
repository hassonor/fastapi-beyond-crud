from fastapi import FastAPI
from src.books.routes import book_router
from src.config import Config
from contextlib import asynccontextmanager
from src.db.main import init_db


@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting...")
    from src.books.models import Book  # noqa
    await init_db()
    yield
    print("server has been stopped")


version = "v1"

app = FastAPI(
    title="Or Hasson Books API",
    description="A REST API for a book review web service",
    version=version,
    lifespan=life_span
)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=['books'])
