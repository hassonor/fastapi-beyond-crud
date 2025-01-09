import pytest
from unittest.mock import patch, AsyncMock
from src.db.main import init_db


@pytest.mark.asyncio
@patch("src.db.main.async_engine")
async def test_init_db(mock_engine):
    mock_engine.begin.return_value.__aenter__.return_value = AsyncMock()
    await init_db()
    mock_engine.begin.assert_called_once()
