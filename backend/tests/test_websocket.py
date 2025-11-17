import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from main import app
from core.database import get_db
from core.config import settings
from models.models import Base

# Создаем тестовую базу данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Заголовок с API ключом для тестов
headers = {"X-API-Key": settings.API_KEY}

class TestWebSocketAPI:
    """Тесты для WebSocket API"""

    def test_websocket_endpoint_available(self):
        """Проверка доступности WebSocket эндпоинта"""
        response = client.get("/webhook/ws")
        assert response.status_code == 404  # WebSocket эндпоинты не доступны через GET

    def test_websocket_stats_endpoint(self):
        """Тест эндпоинта статистики WebSocket"""
        with patch('api.routes.websocket_service') as mock_service:
            mock_service.get_connection_stats.return_value = {
                "total_connections": 1,
                "project_connections": {"test_project": 1}
            }

            response = client.get("/api/websocket/stats", headers=headers)
            assert response.status_code == 200
            assert response.json() == {
                "total_connections": 1,
                "project_connections": {"test_project": 1}
            }

    def test_health_check(self):
        """Проверка health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}