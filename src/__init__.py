from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from contextlib import asynccontextmanager
from src.db.main import init_db, async_engine
from src.db.redis import token_blocklist_client
from .errors import register_all_errors


@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting...")
    from src.db.models import Book  # noqa
    await init_db()
    await token_blocklist_client.connect()
    yield
    await token_blocklist_client.close()
    await async_engine.dispose()
    print("server has been stopped")


version = "v1"

app = FastAPI(
    title="Or Hasson Books API",
    description="A REST API for a book review web service",
    version=version
)

register_all_errors(app)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=['books'])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=['auth'])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=['reviews'])
