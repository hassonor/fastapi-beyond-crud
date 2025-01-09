# File: src/tests/unit/auth/test_auth_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.auth.schemas import UserCreateModel
from src.db.models import User
from src.auth.utils import generate_passwd_hash


@pytest.mark.asyncio
async def test_user_exists_true():
    """
    Your code calls: user_exists -> get_user_by_email -> await session.exec(statement)
    We fix by making session an AsyncMock, so 'await session.exec(...)' works.
    Then the exec(...) return_value has .first() => 'some_user'.
    """
    service = UserService()

    # Use an AsyncMock that behaves like an AsyncSession
    session_mock = AsyncMock(spec=AsyncSession)

    # We want: result = await session.exec(statement)
    # then user = result.first() => 'some_user'
    exec_result_mock = MagicMock()
    # .first() is synchronous in SQLModel, so just use MagicMock
    exec_result_mock.first.return_value = User(
        email="exists@example.com",
        password_hash="fakehash"
    )
    # So session_mock.exec(...) => exec_result_mock
    session_mock.exec.return_value = exec_result_mock

    exists = await service.user_exists("exists@example.com", session_mock)
    assert exists is True


@pytest.mark.asyncio
async def test_user_exists_false():
    """
    If session.exec(...) => result.first() => None => user_exists => False
    """
    service = UserService()
    session_mock = AsyncMock(spec=AsyncSession)

    exec_result_mock = MagicMock()
    exec_result_mock.first.return_value = None
    session_mock.exec.return_value = exec_result_mock

    exists = await service.user_exists("absent@example.com", session_mock)
    assert exists is False


@pytest.mark.asyncio
async def test_create_user():
    """
    Code does:
      session.add(new_user)
      await session.commit()
    => session.commit must be AsyncMock so we don't get "NoneType can't be used in 'await' expression"
    """
    service = UserService()
    session_mock = AsyncMock(spec=AsyncSession)

    # We do not necessarily need to mock .exec, because create_user might not call session.exec...
    # But let's be safe:
    session_mock.exec = AsyncMock()

    # session.add(...) is synchronous in normal usage, so MagicMock is fine
    session_mock.add = MagicMock()
    # But code does 'await session.commit()', so that must be an AsyncMock
    session_mock.commit = AsyncMock(return_value=None)

    user_data = UserCreateModel(
        email="test@example.com",
        password="Secret123",
        first_name="Test",
        last_name="User",
        username="testuser"
    )

    new_user = await service.create_user(user_data, session_mock)
    session_mock.add.assert_called_once()
    session_mock.commit.assert_awaited_once()
    assert new_user.email == "test@example.com"
    # Also check password hashing:
    assert new_user.password_hash != "Secret123"
    assert generate_passwd_hash("Secret123") != new_user.password_hash
