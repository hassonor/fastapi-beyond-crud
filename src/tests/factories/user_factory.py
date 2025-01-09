import uuid
from faker import Faker
from src.auth.models import User
from src.auth.utils import generate_passwd_hash

fake = Faker()


def create_fake_user(
        email: str = None,
        password: str = "fake_password",
        role: str = "user",
        is_verified: bool = False
) -> User:
    """
    Returns a non-committed User instance with realistic random data.
    """
    if email is None:
        email = fake.email()
    return User(
        uid=uuid.uuid4(),
        username=fake.user_name()[:12],  # bigger max length
        email=email,
        password_hash=generate_passwd_hash(password),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        role=role,
        is_verified=is_verified
    )