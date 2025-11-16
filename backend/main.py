from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from core.database import engine, get_db
from models.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создание таблиц
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    yield
    # Shutdown


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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )