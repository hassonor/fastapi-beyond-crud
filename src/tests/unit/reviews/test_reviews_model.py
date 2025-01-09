# File: src/tests/unit/reviews/test_reviews_model.py

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone
from src.db.models import User
from src.db.models import Book
from src.db.models import Review


@pytest.mark.asyncio
async def test_review_model_defaults():
    """
    Basic test of the Review model's defaults and constraints in memory,
    without actually adding to DB. Just verify rating < 5 and fields exist.
    """
    review = Review(rating=3, review_text="Great read!")
    assert review.uid is not None, "UID should auto-generate"
    assert review.rating == 3
    assert review.review_text == "Great read!"
    assert review.user_uid is None
    assert review.book_uid is None
    assert review.created_at is not None
    assert review.updated_at is not None
    # rating < 5 is enforced by pydantic "Field(lt=5)"


@pytest.mark.asyncio
async def test_create_review_in_db(db_session: AsyncSession):
    """
    Create a user, book, and review in the test DB.
    Then read it back and verify correctness.
    """
    # 1) create a user
    new_user = User(
        username="reviewer1",
        email="reviewer@example.com",
        password_hash="fakehash",
        first_name="Review",
        last_name="Tester"
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    # 2) create a book
    new_book = Book(
        title="Test Book",
        author="Test Author",
        publisher="Test Pub",
        published_date=datetime(2021, 1, 1, tzinfo=timezone.utc).date(),
        page_count=123,
        language="EN",
        user_uid=new_user.uid  # if needed
    )
    db_session.add(new_book)
    await db_session.commit()
    await db_session.refresh(new_book)

    # 3) create a review
    review = Review(
        rating=4,
        review_text="Really enjoyed this book!",
        user_uid=new_user.uid,
        book_uid=new_book.uid
    )
    db_session.add(review)
    await db_session.commit()
    await db_session.refresh(review)

    assert review.uid is not None
    assert review.rating == 4
    assert review.user_uid == new_user.uid
    assert review.book_uid == new_book.uid

    # 4) read it back from DB
    stmt = select(Review).where(Review.uid == review.uid)
    result = await db_session.exec(stmt)
    db_review = result.first()
    assert db_review is not None
    assert db_review.review_text == "Really enjoyed this book!"


@pytest.mark.asyncio
async def test_update_review_in_db(db_session: AsyncSession):
    """
    Demonstrate updating an existing review's fields.
    """
    # create a quick user & book
    user = User(username="updater", email="updater@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    book = Book(
        title="Update Book",
        author="Upd Author",
        publisher="Upd Pub",
        published_date=datetime(2020, 5, 5, tzinfo=timezone.utc).date(),
        page_count=222,
        language="EN"
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    # create a review
    review = Review(rating=2, review_text="It was ok", user_uid=user.uid, book_uid=book.uid)
    db_session.add(review)
    await db_session.commit()
    await db_session.refresh(review)

    # now update rating & text
    review.rating = 4
    review.review_text = "Actually, it grew on me"
    await db_session.commit()
    await db_session.refresh(review)

    assert review.rating == 4
    assert review.review_text == "Actually, it grew on me"


@pytest.mark.asyncio
async def test_delete_review_in_db(db_session: AsyncSession):
    """
    Demonstrate deleting a review from the DB.
    """
    # create minimal user & book
    user = User(username="deleter", email="deleter@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    book = Book(title="Delete Book", author="Del Auth", publisher="Del Pub",
                published_date=datetime(2019, 1, 1, tzinfo=timezone.utc).date(),
                page_count=321, language="EN")
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    # create review
    review = Review(rating=1, review_text="Hated it", user_uid=user.uid, book_uid=book.uid)
    db_session.add(review)
    await db_session.commit()
    await db_session.refresh(review)
    rev_uid = review.uid

    # delete
    await db_session.delete(review)
    await db_session.commit()

    # verify
    stmt = select(Review).where(Review.uid == rev_uid)
    result = await db_session.exec(stmt)
    gone = result.first()
    assert gone is None, "Review should be deleted"
