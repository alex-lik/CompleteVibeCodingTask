import os
from typing import List

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agent_task_tracker.db")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # API
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    API_KEY: str = os.getenv("API_KEY", "dev-api-key")

    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()