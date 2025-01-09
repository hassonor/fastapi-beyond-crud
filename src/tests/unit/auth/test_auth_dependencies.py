import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker
from src.auth.utils import create_access_token


# Instead of patching redis.Redis, we patch token_blocklist_client so no real connection happens

@pytest.mark.asyncio
@patch("src.db.redis.token_blocklist_client.token_in_blocklist", new_callable=AsyncMock)
async def test_access_token_bearer_valid(mock_block):
    mock_block.return_value = False
    bearer = AccessTokenBearer()
    token = create_access_token({"email": "test@example.com"}, refresh=False)
    req = AsyncMock()
    req.headers = {"Authorization": f"Bearer {token}"}

    data = await bearer.__call__(req)
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
@patch("src.db.redis.token_blocklist_client.token_in_blocklist", new_callable=AsyncMock)
async def test_access_token_bearer_rejects_refresh(mock_block):
    mock_block.return_value = False
    bearer = AccessTokenBearer()
    token = create_access_token({"email": "test@example.com"}, refresh=True)
    req = AsyncMock()
    req.headers = {"Authorization": f"Bearer {token}"}

    with pytest.raises(HTTPException) as exc:
        await bearer.__call__(req)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
@patch("src.db.redis.token_blocklist_client.token_in_blocklist", new_callable=AsyncMock)
async def test_refresh_token_bearer_valid(mock_block):
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
    mock_block.return_value = False
    bearer = RefreshTokenBearer()
    token = create_access_token({"email": "test@example.com"}, refresh=False)
    req = AsyncMock()
    req.headers = {"Authorization": f"Bearer {token}"}

    with pytest.raises(HTTPException) as exc:
        await bearer.__call__(req)
    assert exc.value.status_code == 403


def test_role_checker_allows():
    checker = RoleChecker(["admin", "user"])
    mock_user = type("User", (), {"role": "user"})()
    assert checker(mock_user) is True


def test_role_checker_denies():
    checker = RoleChecker(["admin"])
    mock_user = type("User", (), {"role": "user"})()
    with pytest.raises(HTTPException) as exc:
        checker(mock_user)
    assert exc.value.status_code == 403
