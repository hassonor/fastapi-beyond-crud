import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.models import Book
from src.books.schemas import BookCreateModel


@pytest.mark.asyncio
async def test_get_all_books():
    """
    If code does:
        statement = select(...)
        result = await session.exec(statement)
        books = result.all()
    => session.exec must be an AsyncMock, so we can await it.
       Then result.all() is sync => MagicMock is fine.
    """
    service = BookService()
    session_mock = AsyncMock(spec=AsyncSession)

    # The return object from session.exec(...) => has .all()
    exec_result_mock = MagicMock()
    exec_result_mock.all.return_value = ["b1", "b2", "b3", "b4"]

    session_mock.exec.return_value = exec_result_mock

    books = await service.get_all_books(session_mock)
    assert len(books) == 4


@pytest.mark.asyncio
async def test_create_book():
    """
    create_book does:
        session.add(...)
        await session.commit()
    => session.commit must be an AsyncMock, session.add can be normal or MagicMock.
    """
    service = BookService()
    session_mock = AsyncMock(spec=AsyncSession)

    # session.add is sync, so MagicMock is fine
    session_mock.add = MagicMock()
    # session.commit is awaited => must be AsyncMock
    session_mock.commit = AsyncMock(return_value=None)

    new_book_data = BookCreateModel(
        title="TestTitle",
        author="TestAuthor",
        publisher="TestPub",
        published_date="2021-01-01",
        page_count=100,
        language="EN"
    )
    created_book = await service.create_book(new_book_data, "bookowner", session_mock)
    session_mock.add.assert_called_once()
    session_mock.commit.assert_awaited_once()

    assert created_book.title == "TestTitle"
    assert created_book.user_uid == "bookowner"


@pytest.mark.asyncio
async def test_delete_book():
    """
    delete_book does:
        book_to_delete = await self.get_book_by_id(...)
        if found:
           await session.delete(book_to_delete)
           await session.commit()
    => session.delete & session.commit must be AsyncMock if they are awaited in the code.
    """
    service = BookService()
    session_mock = AsyncMock(spec=AsyncSession)

    # Step 1: get_book_by_id => session.exec(...) => result.first()
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

    # Step 2: delete & commit must be AsyncMock if your code does:
    #     await session.delete(book_to_delete)
    session_mock.delete = AsyncMock()
    session_mock.commit = AsyncMock(return_value=None)

    deleted = await service.delete_book(str(mock_book.uid), session_mock)
    session_mock.delete.assert_awaited_once_with(mock_book)
    session_mock.commit.assert_awaited_once()
    assert deleted == {}


@pytest.mark.asyncio
async def test_delete_nonexistent_book():
    """
    If get_book_by_id => None => return None from delete_book (no session.delete call).
    """
    service = BookService()
    session_mock = AsyncMock(spec=AsyncSession)

    exec_result_mock = MagicMock()
    exec_result_mock.first.return_value = None
    session_mock.exec.return_value = exec_result_mock

    # session.delete & session.commit are not called if book is None
    session_mock.delete = AsyncMock()
    session_mock.commit = AsyncMock(return_value=None)

    deleted = await service.delete_book("fake-uid", session_mock)
    session_mock.delete.assert_not_awaited()
    session_mock.commit.assert_not_awaited()
    assert deleted is None
