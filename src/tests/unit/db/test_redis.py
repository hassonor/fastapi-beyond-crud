import pytest
from unittest.mock import AsyncMock, patch
from src.db.redis import TokenBlocklistClient


@pytest.mark.asyncio
@patch("src.db.redis.redis.Redis", autospec=True)
async def test_add_jti_to_blocklist(mock_redis):
    mock_redis_instance = AsyncMock()
    mock_redis.return_value = mock_redis_instance
    client = TokenBlocklistClient(expiry=3600)
    await client.add_jti_to_blocklist("test_jti")
    mock_redis_instance.set.assert_awaited_once_with(name="test_jti", value="", ex=3600)


@pytest.mark.asyncio
@patch("src.db.redis.redis.Redis", autospec=True)
async def test_token_in_blocklist(mock_redis):
    mock_redis_instance = AsyncMock()
    mock_redis.return_value = mock_redis_instance
    mock_redis_instance.get.return_value = "blocked"
    client = TokenBlocklistClient()
    blocked = await client.token_in_blocklist("test_jti")
    assert blocked is True
    mock_redis_instance.get.assert_awaited_once_with("test_jti")


@pytest.mark.asyncio
@patch("src.db.redis.redis.Redis", autospec=True)
async def test_connect_success(mock_redis):
    mock_redis_instance = AsyncMock()
    mock_redis.return_value = mock_redis_instance
    mock_redis_instance.ping.return_value = "PONG"

    client = TokenBlocklistClient()
    await client.connect()
    mock_redis_instance.ping.assert_awaited_once()
