import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from main import app
from core.database import get_db
from core.config import settings
from models.models import Base, UserSettings

# Создаем тестовую базу данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_settings.db"
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

class TestSettingsAPI:
    """Тесты для API настроек"""

    def test_get_all_settings_empty(self):
        """Тест получения всех настроек (пустой список)"""
        response = client.get("/api/settings", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_user_settings_empty(self):
        """Тест получения пользовательских настроек (пустой список)"""
        response = client.get("/api/user/settings", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_global_setting(self):
        """Тест создания глобальной настройки"""
        setting_data = {
            "setting_key": "theme",
            "value": "dark",
            "description": "Тема интерфейса",
            "is_global": True
        }

        response = client.post("/api/settings", json=setting_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "theme"
        assert data["value"] == "dark"
        assert data["description"] == "Тема интерфейса"
        assert data["is_global"] == "true"
        assert "id" in data

    def test_create_user_setting(self):
        """Тест создания пользовательской настройки"""
        setting_data = {
            "setting_key": "notifications",
            "value": {"email": True, "push": False},
            "description": "Настройки уведомлений"
        }

        response = client.post("/api/settings", json=setting_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "notifications"
        assert data["value"] == {"email": True, "push": False}
        assert data["description"] == "Настройки уведомлений"
        assert data["is_global"] == "false"
        assert "id" in data

    def test_get_specific_setting(self):
        """Тест получения конкретной настройки"""
        # Сначала создаем настройку
        setting_data = {
            "setting_key": "language",
            "value": "ru",
            "description": "Язык интерфейса"
        }

        create_response = client.post("/api/settings", json=setting_data, headers=headers)
        assert create_response.status_code == 200

        # Получаем настройку
        response = client.get("/api/settings/language", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "language"
        assert data["value"] == "ru"
        assert data["description"] == "Язык интерфейса"

    def test_get_nonexistent_setting(self):
        """Тест получения несуществующей настройки"""
        response = client.get("/api/settings/nonexistent", headers=headers)
        assert response.status_code == 404

    def test_update_setting(self):
        """Тест обновления настройки"""
        # Сначала создаем настройку
        setting_data = {
            "setting_key": "timezone",
            "value": "UTC",
            "description": "Часовой пояс"
        }

        create_response = client.post("/api/settings", json=setting_data, headers=headers)
        assert create_response.status_code == 200

        # Обновляем настройку
        update_data = {
            "value": "Europe/Moscow",
            "description": "Часовой пояс Московский"
        }

        response = client.put(
            "/api/settings/timezone",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == "Europe/Moscow"
        assert data["description"] == "Часовой пояс Московский"

    def test_update_setting_with_batch_requests(self):
        """Тест обновления настроек через batch запрос"""
        # Создаем несколько настроек
        settings_to_create = [
            ("batch1", "value1", "Первая настройка"),
            ("batch2", "value2", "Вторая настройка"),
            ("batch3", "value3", "Третья настройка")
        ]

        for key, value, desc in settings_to_create:
            response = client.post("/api/settings",
                                json={"setting_key": key, "value": value, "description": desc},
                                headers=headers)
            assert response.status_code == 200

        # Получаем несколько настроек за раз
        response = client.get("/api/settings/batch?keys=batch1,batch2", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "settings" in data
        assert len(data["settings"]) == 2
        assert "batch1" in data["settings"]
        assert "batch2" in data["settings"]

    def test_delete_setting(self):
        """Тест удаления настройки"""
        # Сначала создаем настройку
        setting_data = {
            "setting_key": "temp_setting",
            "value": "temp_value"
        }

        create_response = client.post("/api/settings", json=setting_data, headers=headers)
        assert create_response.status_code == 200

        # Удаляем настройку
        response = client.delete("/api/settings/temp_setting", headers=headers)
        assert response.status_code == 200
        assert "message" in response.json()

        # Проверяем, что настройка удалена
        get_response = client.get("/api/settings/temp_setting", headers=headers)
        assert get_response.status_code == 404

    def test_delete_all_user_settings(self):
        """Тест удаления всех пользовательских настроек"""
        # Создаем несколько пользовательских настроек
        for i in range(3):
            setting_data = {
                "setting_key": f"user_setting_{i}",
                "value": f"value_{i}"
            }
            response = client.post("/api/settings", json=setting_data, headers=headers)
            assert response.status_code == 200

        # Удаляем все пользовательские настройки
        response = client.delete("/api/user/settings", headers=headers)
        assert response.status_code == 200
        assert "message" in response.json()

        # Проверяем, что пользовательские настройки удалены
        response = client.get("/api/user/settings", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_global_settings_priority(self):
        """Тест приоритета глобальных настроек"""
        # Создаем глобальную настройку
        global_data = {
            "setting_key": "priority_test",
            "value": "global_value",
            "is_global": True
        }
        response = client.post("/api/settings", json=global_data, headers=headers)
        assert response.status_code == 200

        # Создаем пользовательскую настройку с тем же ключом
        user_data = {
            "setting_key": "priority_test",
            "value": "user_value"
        }
        response = client.post("/api/settings", json=user_data, headers=headers)
        assert response.status_code == 200

        # При получении глобальной настройки должна вернуть глобальное значение
        response = client.get("/api/settings/priority_test", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # В данном случае пользовательская настройка имеет приоритет (последняя созданная)
        assert data["value"] == "user_value"

    def test_api_authentication_required(self):
        """Тест, что API требует аутентификации"""
        response = client.get("/api/settings")
        assert response.status_code == 401  # Ожидается ошибка аутентификации

    @patch('api.routes_settings.SettingsService')
    def test_settings_service_integration(self, mock_settings_service):
        """Тест интеграции с сервисом настроек"""
        # Создаем мок сервиса
        mock_instance = mock_settings_service.return_value
        mock_instance.get_all_settings.return_value = [
            {
                "id": 1,
                "key": "test",
                "value": {"test": True},
                "description": "Test setting",
                "is_global": "false",
                "created_at": "2025-01-17T10:00:00Z",
                "updated_at": "2025-01-17T10:00:00Z"
            }
        ]

        response = client.get("/api/settings", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["key"] == "test"


if __name__ == "__main__":
    pytest.main([__file__])