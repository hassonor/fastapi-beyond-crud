# File: src/tests/unit/reviews/test_reviews_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlmodel.ext.asyncio.session import AsyncSession
from src.reviews.service import ReviewService
from src.db.models import Review, Book, User
from src.reviews.schemas import ReviewCreateModel
from fastapi import HTTPException, status


@pytest.mark.asyncio
@patch("src.reviews.service.book_service.get_book_by_id")
@patch("src.reviews.service.user_service.get_user_by_email")
async def test_add_review_to_book_success(mock_get_user, mock_get_book):
    service = ReviewService()
    session_mock = AsyncMock(spec=AsyncSession)
    dummy_book = Book(title="Reviewable Book")
    dummy_user = User(email="reviewer@example.com", password_hash="fakehash")

    mock_get_book.return_value = dummy_book
    mock_get_user.return_value = dummy_user
    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock()

    review_data = ReviewCreateModel(rating=4, review_text="Great read!")
    new_review = await service.add_review_to_book(
        user_email="reviewer@example.com",
        book_uid="fake-book-uid",
        review_data=review_data,
        session=session_mock
    )
    session_mock.add.assert_called_once()
    session_mock.commit.assert_awaited_once()
    assert new_review.review_text == "Great read!"
    assert new_review.rating == 4
    assert new_review.book == dummy_book
    assert new_review.user == dummy_user


@pytest.mark.asyncio
async def test_get_review_found():
    service = ReviewService()
    session_mock = AsyncMock(spec=AsyncSession)
    exec_result = MagicMock()
    exec_result.first.return_value = Review(rating=4, review_text="Some text")
    session_mock.exec.return_value = exec_result
    review = await service.get_review("some-uid", session_mock)
    assert review is not None
    assert review.review_text == "Some text"


@pytest.mark.asyncio
async def test_get_all_reviews():
    service = ReviewService()
    session_mock = AsyncMock(spec=AsyncSession)
    exec_result = MagicMock()
    exec_result.all.return_value = [
        Review(rating=1, review_text="Bad"),
        Review(rating=4, review_text="Nice")
    ]
    session_mock.exec.return_value = exec_result
    all_reviews = await service.get_all_reviews(session_mock)
    assert len(all_reviews) == 2


@pytest.mark.asyncio
@patch("src.reviews.service.user_service.get_user_by_email")
async def test_delete_review_to_from_book_forbidden(mock_get_user):
    service = ReviewService()
    session_mock = AsyncMock(spec=AsyncSession)
    user_current = User(email="currentuser@example.com")
    mock_get_user.return_value = user_current

    dummy_review = Review(rating=3, review_text="Ok book")
    dummy_review.user = User(email="someoneelse@example.com")

    exec_result = MagicMock()
    exec_result.first.return_value = dummy_review
    session_mock.exec.return_value = exec_result

    with pytest.raises(HTTPException) as exc:
        await service.delete_review_to_from_book(
            review_uid="some-review",
            user_email="currentuser@example.com",
            session=session_mock
        )
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Cannot delete this review" in str(exc.value)
