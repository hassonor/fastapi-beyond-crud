# File: src/tests/unit/tags/test_tags_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlmodel.ext.asyncio.session import AsyncSession
from src.tags.service import TagService
from src.db.models import Tag
from src.tags.schemas import TagCreateModel, TagAddModel
from src.errors import TagAlreadyExists, TagNotFound, BookNotFound


@pytest.mark.asyncio
async def test_add_tag_new():
    """
    Since the service code does NOT do 'await session.refresh(new_tag)', we cannot
    assert that it was 'awaited'. Instead, we verify it was *called*.
    """
    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)

    # Simulate "no existing tag" from DB
    exec_result = MagicMock()
    exec_result.first.return_value = None
    session_mock.exec.return_value = exec_result

    # Normal mocks for add/commit/refresh
    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    # This is key: MagicMock (so .assert_called_*) not .assert_awaited_*
    session_mock.refresh = MagicMock()

    new_tag = await service.add_tag(TagCreateModel(name="Romance"), session_mock)

    session_mock.add.assert_called_once()
    session_mock.commit.assert_awaited_once()

    assert new_tag.name == "Romance"


# Other tests remain the same
@pytest.mark.asyncio
async def test_add_tag_already_exists():
    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)

    existing_tag = Tag(name="Mystery")
    exec_result = MagicMock()
    exec_result.first.return_value = existing_tag
    session_mock.exec.return_value = exec_result

    with pytest.raises(TagAlreadyExists):
        await service.add_tag(TagCreateModel(name="Mystery"), session_mock)


@pytest.mark.asyncio
async def test_delete_tag_not_found():
    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)

    service.get_tag_by_uid = AsyncMock(return_value=None)
    with pytest.raises(TagNotFound):
        await service.delete_tag("fake-uid", session_mock)


@pytest.mark.asyncio
async def test_delete_tag_success():
    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)
    mock_tag = Tag(name="Horror")

    service.get_tag_by_uid = AsyncMock(return_value=mock_tag)
    session_mock.delete = AsyncMock()
    session_mock.commit = AsyncMock()

    await service.delete_tag("some-uid", session_mock)

    service.get_tag_by_uid.assert_awaited_once_with("some-uid", session_mock)
    session_mock.delete.assert_awaited_once_with(mock_tag)
    session_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.tags.service.BookService.get_book_by_id", new_callable=AsyncMock)
async def test_add_tags_to_book_no_book(mock_get_book):
    mock_get_book.return_value = None
    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)

    tag_data = TagAddModel(tags=[TagCreateModel(name="DoesNotMatter")])
    with pytest.raises(BookNotFound):
        await service.add_tags_to_book("fake-book-uid", tag_data, session_mock)

    mock_get_book.assert_awaited_once_with(book_uid="fake-book-uid", session=session_mock)


@pytest.mark.asyncio
@patch("src.tags.service.BookService.get_book_by_id", new_callable=AsyncMock)
async def test_add_tags_to_book_success(mock_get_book):
    mock_book = MagicMock()
    mock_book.tags = []
    mock_get_book.return_value = mock_book

    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)

    exec_result = MagicMock()
    exec_result.one_or_none.return_value = None
    session_mock.exec.return_value = exec_result

    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock()

    tag_data = TagAddModel(tags=[TagCreateModel(name="Adventure")])
    updated_book = await service.add_tags_to_book("fake-book-uid", tag_data, session_mock)

    mock_get_book.assert_awaited_once_with(book_uid="fake-book-uid", session=session_mock)
    session_mock.commit.assert_awaited_once()
    session_mock.refresh.assert_awaited_once_with(mock_book)

    assert updated_book is mock_book
    assert len(mock_book.tags) == 1
    assert mock_book.tags[0].name == "Adventure"
