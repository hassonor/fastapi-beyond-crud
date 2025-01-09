# File: src/tests/unit/books/test_books_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.books.models import Book
from src.books.schemas import BookCreateModel


@pytest.mark.asyncio
async def test_get_all_books():
    """
    Code does: statement = select(...); result = await session.exec(statement); books = result.all()
    => session.exec must be AsyncMock; result.all() is sync => MagicMock
    """
    service = BookService()
    session_mock = AsyncMock(spec=AsyncSession)

    # The returned object from session.exec(...) => a sync mock that has .all()
    exec_result_mock = MagicMock()
    exec_result_mock.all.return_value = ["b1", "b2", "b3", "b4"]

    # So session_mock.exec(...) => exec_result_mock
    session_mock.exec.return_value = exec_result_mock

    books = await service.get_all_books(session_mock)
    assert len(books) == 4


@pytest.mark.asyncio
async def test_create_book():
    """
    create_book does:
      session.add(new_book)
      await session.commit()
    => session.commit must be an AsyncMock
    => session.add can be MagicMock or normal
    """
    service = BookService()
    session_mock = AsyncMock(spec=AsyncSession)
    session_mock.exec = AsyncMock()  # in case there's a check

    # add is sync, commit is awaited
    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock(return_value=None)

    new_book_data = BookCreateModel(
        title="TestTitle",
        author="TestAuthor",
        publisher="TestPub",
        published_date="2021-01-01",
        page_count=100,
        language="EN"
    )
    created = await service.create_book(new_book_data, "bookowner", session_mock)
    session_mock.add.assert_called_once()
    session_mock.commit.assert_awaited_once()

    assert created.title == "TestTitle"
    assert created.user_uid == "bookowner"


@pytest.mark.asyncio
async def test_delete_book():
    """
    delete_book calls get_book_by_id => await session.exec(...) => result.first()
    Then if book found: session.delete(book), await session.commit()
    """
    service = BookService()
    session_mock = AsyncMock(spec=AsyncSession)

    # Mock session.exec => object with .first() => a Book
    exec_result_mock = MagicMock()
    mock_book = Book(
        title="DelBook",
        author="DelAuthor",
        publisher="Pub",
        published_date="2021-01-01",
        page_count=100,
        language="EN"
    )
    exec_result_mock.first.return_value = mock_book
    session_mock.exec.return_value = exec_result_mock

    # session.delete is sync, session.commit is awaited
    session_mock.delete = MagicMock()
    session_mock.commit = AsyncMock(return_value=None)

    deleted = await service.delete_book(str(mock_book.uid), session_mock)
    session_mock.delete.assert_called_once_with(mock_book)
    session_mock.commit.assert_awaited_once()
    assert deleted == {}


@pytest.mark.asyncio
async def test_delete_nonexistent_book():
    """
    If get_book_by_id => None => return None from delete_book
    """
    service = BookService()
    session_mock = AsyncMock(spec=AsyncSession)

    exec_result_mock = MagicMock()
    exec_result_mock.first.return_value = None
    session_mock.exec.return_value = exec_result_mock

    session_mock.delete = MagicMock()
    session_mock.commit = AsyncMock(return_value=None)

    deleted = await service.delete_book("fake-uid", session_mock)
    session_mock.delete.assert_not_called()
    session_mock.commit.assert_not_awaited()
    assert deleted is None
