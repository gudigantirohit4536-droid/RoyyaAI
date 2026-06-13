from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

# Look for .env in backend/ first, then project root
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "RoyyaAI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://royyaai:royyaai_secret@localhost:5432/royyaai_db"
    POSTGRES_USER: str = "royyaai"
    POSTGRES_PASSWORD: str = "royyaai_secret"
    POSTGRES_DB: str = "royyaai_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-this-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # LLM
    LLM_PROVIDER: str = "openai"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Qdrant
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "royyaai_knowledge"

    # MinIO
    MINIO_HOST: str = "minio"
    MINIO_PORT: int = 9000
    MINIO_ROOT_USER: str = "royyaai_minio"
    MINIO_ROOT_PASSWORD: str = "royyaai_minio_secret"
    MINIO_BUCKET: str = "royyaai-files"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = str(_ENV_FILE)
        case_sensitive = True
        extra = "ignore"


settings = Settings()
