"""
Application configuration and settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    APP_NAME: str = "MMM Dashboard API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str
    
    # Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # MMM Configuration
    MMM_MODEL_PATH: str = "data/models/saved_mmm.pkl"
    USE_MOCK_DATA: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def MMM_MODEL_FULL_PATH(self) -> Path:
        """Get full path to MMM model file."""
        return Path(__file__).parent.parent.parent / self.MMM_MODEL_PATH

    model_config = {
        "env_file": "../../.env.local",
        "extra": "ignore",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
