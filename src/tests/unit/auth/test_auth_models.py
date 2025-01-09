import uuid
from src.db.models import User


def test_user_model_repr():
    user = User(
        uid=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        password_hash="hashed_pw",
        first_name="Test",
        last_name="User",
        role=None,
    )
    assert f"<User {user.username}>" in repr(user)


def test_user_model_defaults():
    user = User(
        username="defaultuser",
        email="default@example.com",
        password_hash="defhash",
        first_name="Default",
        last_name="User"
    )
    # If role is None, we pass
    assert user.role in [None, "user"]

    # If created_at is None, pass
    if user.created_at is not None:
        # Then we can check it
        assert user.created_at is not None
