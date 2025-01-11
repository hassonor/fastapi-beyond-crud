import uuid
from faker import Faker
from src.db.models import Review

fake = Faker()


def create_fake_review(user_uid=None, book_uid=None) -> Review:
    return Review(
        uid=uuid.uuid4(),
        rating=fake.random_int(min=1, max=4),  # rating < 5
        review_text=fake.sentence(nb_words=10),
        user_uid=user_uid,
        book_uid=book_uid
    )
