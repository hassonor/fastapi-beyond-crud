from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
    DB_HOST_TO_PG: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    DOMAIN: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


Config = Settings()
