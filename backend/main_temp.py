from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from core.config import settings
from core.database import engine, get_db
from models.models import Base
from api.routes_temp import api_router
from api.routes_settings_temp import settings_router

# Создаем базовые таблицы при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agent Task Tracker API",
    description="API для отслеживания задач AI-агентов",
    version="1.0.0",
)

# CORS middleware для frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3053", "http://localhost:3050", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(settings_router, prefix="/api", tags=["settings"])

@app.get("/")
async def root():
    return {"message": "Agent Task Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)