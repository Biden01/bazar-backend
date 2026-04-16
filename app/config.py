from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://bazar:bazar_secret@db:5432/bazar_digital"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    CORS_ORIGINS: str = "*"
    DEV_MODE: bool = True
    SERVER_URL: str = "http://localhost:8000"
    ADMIN_SECRET: str = "change-me-admin-secret"
    OTP_RATE_LIMIT: str = "5/minute"
    OTP_MAX_ATTEMPTS: int = 5
    OTP_ATTEMPTS_WINDOW: int = 600  # seconds (10 min)
    OPENAI_API_KEY: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
