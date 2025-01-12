# File: src/tests/unit/auth/test_auth_dependencies.py

import pytest
from unittest.mock import AsyncMock, patch
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker
from src.auth.utils import create_access_token
from src.errors import (
    AccessTokenRequired,
    RefreshTokenRequired,
    InsufficientPermission,
)


@pytest.mark.asyncio
@patch("src.db.redis.token_blocklist_client.token_in_blocklist", new_callable=AsyncMock)
async def test_access_token_bearer_valid(mock_block):
    """
    If token is a valid ACCESS token (refresh=False) and not blocked,
    we expect no exception, returning token data.
    """
    mock_block.return_value = False
    bearer = AccessTokenBearer()
    token = create_access_token({"email": "test@example.com"}, refresh=False)
    req = AsyncMock()
    req.headers = {"Authorization": f"Bearer {token}"}

    data = await bearer.__call__(req)
    assert data["user"]["email"] == "test@example.com"
    assert data["refresh"] is False


@pytest.mark.asyncio
@patch("src.db.redis.token_blocklist_client.token_in_blocklist", new_callable=AsyncMock)
async def test_access_token_bearer_rejects_refresh(mock_block):
    """
    If token is a REFRESH token (refresh=True) but AccessTokenBearer is used,
    your code raises AccessTokenRequired (a custom exception).
    """
    mock_block.return_value = False
    bearer = AccessTokenBearer()
    token = create_access_token({"email": "test@example.com"}, refresh=True)
    req = AsyncMock()
    req.headers = {"Authorization": f"Bearer {token}"}

    # Expect AccessTokenRequired, not HTTPException
    with pytest.raises(AccessTokenRequired):
        await bearer.__call__(req)


@pytest.mark.asyncio
@patch("src.db.redis.token_blocklist_client.token_in_blocklist", new_callable=AsyncMock)
async def test_refresh_token_bearer_valid(mock_block):
    """
    If token is a valid REFRESH token (refresh=True) and not blocked,
    we expect no exception, returning token data.
    """
    mock_block.return_value = False
    bearer = RefreshTokenBearer()
    token = create_access_token({"email": "test@example.com"}, refresh=True)
    req = AsyncMock()
    req.headers = {"Authorization": f"Bearer {token}"}

    data = await bearer.__call__(req)
    assert data["user"]["email"] == "test@example.com"
    assert data["refresh"] is True


@pytest.mark.asyncio
@patch("src.db.redis.token_blocklist_client.token_in_blocklist", new_callable=AsyncMock)
async def test_refresh_token_bearer_rejects_access(mock_block):
    """
    If token is an ACCESS token (refresh=False) but RefreshTokenBearer is used,
    your code raises RefreshTokenRequired (a custom exception).
    """
    mock_block.return_value = False
    bearer = RefreshTokenBearer()
    token = create_access_token({"email": "test@example.com"}, refresh=False)
    req = AsyncMock()
    req.headers = {"Authorization": f"Bearer {token}"}

    # Expect RefreshTokenRequired, not HTTPException
    with pytest.raises(RefreshTokenRequired):
        await bearer.__call__(req)


def test_role_checker_allows():
    """
    If user's role is in the allowed list, no exception is raised (returns True).
    """
    checker = RoleChecker(["admin", "user"])
    mock_user = type("User", (), {"role": "user"})()
    assert checker(mock_user) is True


def test_role_checker_denies():
    """
    If user's role is NOT in the allowed list, your code raises InsufficientPermission
    (a custom exception).
    """
    checker = RoleChecker(["admin"])
    mock_user = type("User", (), {"role": "user"})()
    with pytest.raises(InsufficientPermission):
        checker(mock_user)
