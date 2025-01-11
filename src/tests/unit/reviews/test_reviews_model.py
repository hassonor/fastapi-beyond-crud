# File: src/tests/unit/reviews/test_reviews_model.py

import uuid
from datetime import datetime
from src.db.models import Review


def test_review_repr():
    review_uid = uuid.uuid4()
    user_uid = uuid.uuid4()
    book_uid = uuid.uuid4()
    review = Review(
        uid=review_uid,
        rating=4,
        review_text="Excellent!",
        user_uid=user_uid,
        book_uid=book_uid
    )
    assert f"<Review for book {book_uid} by user {user_uid}>" in repr(review)


def test_review_defaults():
    review = Review(
        rating=2,
        review_text="Not bad"
    )
    # created_at might be None or datetime
    if review.created_at is not None:
        assert isinstance(review.created_at, datetime)
