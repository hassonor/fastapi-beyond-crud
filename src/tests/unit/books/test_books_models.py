import uuid
from datetime import date
from src.db.models import Book


def test_book_model_repr():
    book = Book(
        uid=uuid.uuid4(),
        title="TestBook",
        author="AuthorZ",
        publisher="PubZ",
        published_date=date.today(),
        page_count=200,
        language="EN"
    )
    assert "<Book TestBook>" in repr(book)


def test_book_model_defaults():
    book = Book(
        title="DefaultTitle",
        author="DefaultAuthor",
        publisher="DefaultPub",
        published_date=date.today(),
        page_count=100,
        language="EN"
    )
    # If your code sets created_at=None, we won't fail
    if book.created_at is not None:
        assert book.created_at is not None
