import pytest
from src.db.redis import TokenBlocklistClient


@pytest.mark.asyncio
async def test_add_jti_to_blocklist(mock_redis):
    """Test adding JTI to blocklist"""
    # Use the globally mocked Redis from conftest.py
    client = TokenBlocklistClient()
    client.redis = mock_redis

    await client.add_jti_to_blocklist("test-jti")

    # Verify the JTI was added
    result = await mock_redis.get("test-jti")
    assert result is not None


@pytest.mark.asyncio
async def test_token_in_blocklist(mock_redis):
    """Test checking if token is in blocklist"""
    # Use the globally mocked Redis from conftest.py
    client = TokenBlocklistClient()
    client.redis = mock_redis

    # Add token to blocklist
    await mock_redis.set("test-jti", "")

    # Check if token is in blocklist
    is_blocked = await client.token_in_blocklist("test-jti")
    assert is_blocked is True

    # Check non-existent token
    is_blocked = await client.token_in_blocklist("non-existent")
    assert is_blocked is False


@pytest.mark.asyncio
async def test_connect_success(mock_redis):
    """Test successful connection"""
    # Use the globally mocked Redis from conftest.py
    client = TokenBlocklistClient()
    client.redis = mock_redis

    await client.connect()
    pong = await mock_redis.ping()
    assert pong is True
