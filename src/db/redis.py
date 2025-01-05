import logging
import redis.asyncio as redis

from src.config import Config

logger = logging.getLogger(__name__)


class TokenBlocklistClient:
    """
    A class-based Redis client for managing blocked JTIs (token IDs).
    """

    def __init__(self, expiry: int = 3600):
        self.expiry = expiry
        # Create an async Redis client
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=0,
            decode_responses=True
        )

    async def connect(self) -> None:
        """
        Attempt a Redis PING to ensure connectivity.
        Raises an exception if the connection fails.
        """
        try:
            await self.redis.ping()
            logger.info("Connected to Redis.")
        except Exception as e:
            logger.exception("Failed to connect to Redis: %s", e)
            raise

    async def add_jti_to_blocklist(self, jti: str) -> None:
        """
        Block a token JTI by storing it in Redis with an expiry.
        """
        await self.redis.set(name=jti, value="", ex=self.expiry)
        logger.debug("Added JTI '%s' to blocklist with expiry %s seconds.", jti, self.expiry)

    async def token_in_blocklist(self, jti: str) -> bool:
        """
        Check if a token JTI exists in Redis. If it does,
        we consider the token blocked/revoked.
        """
        result = await self.redis.get(jti)
        return result is not None

    async def close(self) -> None:
        """
        Close the Redis connection gracefully.
        """
        await self.redis.close()
        logger.info("Redis connection closed.")


token_blocklist_client = TokenBlocklistClient()
