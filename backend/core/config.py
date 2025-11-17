import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./agent_tracker.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # API
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    BASE_URL: str = f"http://localhost:8002"

    # Security
    SECRET_KEY: str = "dev-secret-key"
    API_KEY: str = "dev-api-key"

    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()