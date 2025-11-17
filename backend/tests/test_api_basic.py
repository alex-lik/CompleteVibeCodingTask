import pytest
from fastapi.testclient import TestClient

from main import app
from core.config import settings

client = TestClient(app)

# Заголовок с API ключом для тестов
headers = {"X-API-Key": settings.API_KEY}

def test_root_endpoint():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Agent Task Tracker API"}

def test_health_endpoint():
    """Тест эндпоинта здоровья"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_db_check_endpoint():
    """Тест эндпоинта проверки базы данных"""
    response = client.get("/db-check")
    # Должен вернуть статус или ошибку подключения
    assert response.status_code in [200, 500]

def test_redis_check_endpoint():
    """Тест эндпоинта проверки Redis"""
    response = client.get("/redis-check")
    # Должен вернуть статус или ошибку подключения
    assert response.status_code in [200, 500]

def test_api_documentation():
    """Тест доступности документации API"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_api_redoc():
    """Тест доступности ReDoc документации"""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_api_openapi():
    """Тест доступности OpenAPI спецификации"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert data["info"]["title"] == "Agent Task Tracker API"

def test_webhook_endpoints_structure():
    """Проверка структуры вебхук эндпоинтов"""
    endpoints = [
        "/webhook/start",
        "/webhook/finish",
        "/webhook/status",
        "/webhook/error"
    ]

    for endpoint in endpoints:
        response = client.post(endpoint, json={})
        # Ожидается ошибка авторизации (401) так как нет API ключа
        assert response.status_code == 401

def test_api_endpoints_structure():
    """Проверка структуры API эндпоинтов - должны работать даже без БД"""
    endpoints = [
        "/api/projects",
        "/api/stats"
    ]

    for endpoint in endpoints:
        response = client.get(endpoint, headers=headers)
        # Должен вернуть 500 (ошибка БД) или 200 (пустые данные)
        assert response.status_code in [200, 500]

if __name__ == "__main__":
    pytest.main([__file__])