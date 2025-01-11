# File: src/tests/factories/book_factory.py

import uuid
from datetime import date, timedelta
from faker import Faker
from src.db.models import Book

fake = Faker()


def create_fake_book(user_uid=None, allow_future_date=False, min_pages=50) -> Book:
    pub_date = date.today()
    if allow_future_date:
        pub_date += timedelta(days=fake.random_int(min=1, max=365))

    return Book(
        uid=uuid.uuid4(),
        title=fake.sentence(nb_words=4),
        author=fake.name(),
        publisher=fake.company(),
        published_date=pub_date,
        page_count=fake.random_int(min=min_pages, max=1500),
        language="EN",
        user_uid=user_uid
    )
