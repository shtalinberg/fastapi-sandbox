"""
Core configuration settings for FastAPI application.
"""


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    # Project info
    PROJECT_NAME: str = Field(default="FastAPI Sandbox")
    DEBUG: bool = Field(default=True)
    API_V1_STR: str = Field(default="/api/v1")

    # Database
    DATABASE_URL: str = Field(
        default=(
            "postgresql+psycopg://fasandbox_user:fasandbox_pass@postgres:5432/"
            "fasandbox_db"
        )
    )
    ASYNC_DATABASE_URL: str = Field(
        default=(
            "postgresql+psycopg://fasandbox_user:fasandbox_pass@postgres:5432/"
            "fasandbox_db"
        )
    )

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")

    # External API
    EXTERNAL_API_URL: str = Field(default="https://jsonplaceholder.typicode.com")
    SYNC_INTERVAL_MINUTES: int = Field(default=60)

    # Database naming convention for constraints
    DB_NAMING_CONVENTION: dict[str, str] = Field(
        default={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


# Global settings instance
settings = Settings()
