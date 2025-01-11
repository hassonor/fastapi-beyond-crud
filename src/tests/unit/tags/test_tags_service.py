# File: src/tests/unit/tags/test_tags_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlmodel.ext.asyncio.session import AsyncSession
from src.tags.service import TagService
from src.db.models import Tag
from src.tags.schemas import TagCreateModel, TagAddModel
from src.errors import TagAlreadyExists, TagNotFound, BookNotFound


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
async def test_add_tag_new():
    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)
    exec_result = MagicMock()
    exec_result.first.return_value = None
    session_mock.exec.return_value = exec_result
    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock()

    new_tag = await service.add_tag(TagCreateModel(name="Romance"), session_mock)
    session_mock.add.assert_called_once()
    assert new_tag.name == "Romance"


@pytest.mark.asyncio
async def test_delete_tag_not_found():
    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)

    # .get_tag_by_uid => none => raise TagNotFound
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

    # Should not raise
    await service.delete_tag("some-uid", session_mock)
    session_mock.delete.assert_awaited_once_with(mock_tag)
    session_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_tags_to_book_no_book():
    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)

    # We'll patch book_service.get_book => None => raise BookNotFound
    service.book_service = MagicMock()
    service.book_service.get_book = AsyncMock(return_value=None)

    with pytest.raises(BookNotFound):
        await service.add_tags_to_book("fake-book-uid", TagAddModel(), session_mock)


@pytest.mark.asyncio
async def test_add_tags_to_book_success():
    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)

    mock_book = MagicMock()
    mock_book.tags = []
    service.book_service = MagicMock()
    service.book_service.get_book = AsyncMock(return_value=mock_book)

    # We'll say the DB has no tag => create new
    exec_result = MagicMock()
    exec_result.one_or_none.return_value = None
    session_mock.exec.return_value = exec_result

    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock()

    tag_data = TagAddModel()
    tag_data.tags = [TagCreateModel(name="Adventure")]

    updated_book = await service.add_tags_to_book("fake-book-uid", tag_data, session_mock)
    assert updated_book == mock_book
    session_mock.commit.assert_awaited_once()
    session_mock.refresh.assert_awaited_once_with(mock_book)
    assert len(mock_book.tags) == 1
    assert mock_book.tags[0].name == "Adventure"


@pytest.mark.asyncio
async def test_update_tag_success():
    service = TagService()
    session_mock = AsyncMock(spec=AsyncSession)
    mock_tag = Tag(name="OldName")
    service.get_tag_by_uid = AsyncMock(return_value=mock_tag)

    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock()

    updated_tag = await service.update_tag("fake-uid", TagCreateModel(name="NewName"), session_mock)
    session_mock.commit.assert_awaited()
    session_mock.refresh.assert_awaited_once_with(mock_tag)
    assert updated_tag.name == "NewName"
