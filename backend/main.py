from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from core.database import engine, get_db
from core.redis import redis_client
from models.models import Base
from webhook.routes import webhook_router
# from webhook.websocket_routes import websocket_router  # Временно отключен


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создание таблиц
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

    # Подключение к Redis
    print("Connecting to Redis...")
    await redis_client.connect()

    yield
    # Shutdown: отключение от Redis
    print("Disconnecting from Redis...")
    await redis_client.disconnect()


app = FastAPI(
    title="Agent Task Tracker API",
    description="API для отслеживания задач AI-агентов",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение webhook роутеров
app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])
# app.include_router(websocket_router, prefix="/webhook", tags=["websocket"])  # Временно отключен


@app.get("/")
async def root():
    return {"message": "Agent Task Tracker API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/db-check")
async def db_check():
    """Проверка подключения к базе данных"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
        return {
            "status": "connected",
            "database": settings.DATABASE_URL.split('@')[1],
            "version": version
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/redis-check")
async def redis_check():
    """Проверка подключения к Redis"""
    try:
        if not redis_client.redis:
            await redis_client.connect()

        # Тестовая операция
        await redis_client.set("test_key", "test_value", expire=10)
        test_result = await redis_client.get("test_key")

        # Получение информации о Redis
        info = await redis_client.redis.info()

        return {
            "status": "connected",
            "redis_url": settings.REDIS_URL,
            "version": info.get("redis_version"),
            "test_operation": "success" if test_result == "test_value" else "failed",
            "used_memory": info.get("used_memory_human")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )