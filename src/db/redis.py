import logging
import redis.asyncio as redis

from src.config import Config

logger = logging.getLogger(__name__)


class TokenBlocklistClient:
    """
    A class-based Redis client for managing blocked JTIs (token IDs).
    """

    def __init__(self, expiry: int = 86400):
        """
        :param expiry: Time-to-live in seconds for each JTI (default: 1 day).
                      Increase or decrease as needed.
        """
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
            pong = await self.redis.ping()
            logger.info("Redis PING response: %s", pong)
            logger.info("Connected to Redis at %s:%s (db=0)", Config.REDIS_HOST, Config.REDIS_PORT)
        except Exception as e:
            logger.exception("Failed to connect to Redis: %s", e)
            raise

    async def add_jti_to_blocklist(self, jti: str) -> None:
        """
        Block a token JTI by storing it in Redis with an expiry.
        """
        result = await self.redis.set(name=jti, value="", ex=self.expiry)
        logger.info("SET JTI '%s': result=%s", jti, result)
        logger.debug("Added JTI '%s' to blocklist with expiry %s seconds.", jti, self.expiry)

    async def token_in_blocklist(self, jti: str) -> bool:
        """
        Check if a token JTI exists in Redis. If it does,
        we consider the token blocked/revoked.
        """
        result = await self.redis.get(jti)
        logger.debug("GET JTI '%s': returned=%s", jti, result)
        return result is not None

    async def close(self) -> None:
        """
        Close the Redis connection gracefully.
        """
        await self.redis.close()
        logger.info("Redis connection closed.")


token_blocklist_client = TokenBlocklistClient()
