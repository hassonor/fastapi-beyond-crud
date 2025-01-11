import uuid
from faker import Faker
from src.db.models import Tag

fake = Faker()


def create_fake_tag() -> Tag:
    return Tag(
        uid=uuid.uuid4(),
        name=fake.word()
    )
