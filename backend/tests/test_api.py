import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from main import app
from core.database import get_db, Base
from core.config import settings
from models.models import Project, Task, Agent

# Создаем тестовую базу данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

@pytest.fixture(scope="function")
def setup_test_db():
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)

    # Добавляем тестовые данные
    db = TestingSessionLocal()

    # Тестовый проект
    project = Project(name="test_project")
    db.add(project)

    # Тестовый агент
    agent = Agent(name="test_agent")
    db.add(agent)

    db.commit()
    db.refresh(project)
    db.refresh(agent)

    # Тестовые задачи
    task1 = Task(
        task_id="task_1",
        title="Test Task 1",
        description="Test Task 1 Description",
        status="completed",
        project_id=project.id,
        agent_id=agent.id,
        started_at="2024-01-01T10:00:00",
        finished_at="2024-01-01T10:30:00",
        duration_seconds=1800,
        result="Test result"
    )

    task2 = Task(
        task_id="task_2",
        title="Test Task 2",
        description="Test Task 2 Description",
        status="running",
        project_id=project.id,
        agent_id=agent.id,
        started_at="2024-01-01T11:00:00"
    )

    db.add(task1)
    db.add(task2)
    db.commit()

    yield

    # Очистка после теста
    db.close()
    Base.metadata.drop_all(bind=engine)

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

def test_get_projects(setup_test_db):
    """Тест получения списка проектов"""
    response = client.get("/api/projects", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "test_project"

def test_get_project(setup_test_db):
    """Тест получения информации о проекте"""
    response = client.get("/api/projects/test_project", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_project"

def test_get_nonexistent_project(setup_test_db):
    """Тест получения несуществующего проекта"""
    response = client.get("/api/projects/nonexistent", headers=headers)
    assert response.status_code == 404

def test_get_project_tasks(setup_test_db):
    """Тест получения задач проекта"""
    response = client.get("/api/projects/test_project/tasks", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Задачи должны быть отсортированы по дате создания (новые первыми)
    assert data[0]["status"] == "running"
    assert data[1]["status"] == "completed"

def test_get_project_tasks_with_filter(setup_test_db):
    """Тест получения задач проекта с фильтрацией"""
    response = client.get("/api/projects/test_project/tasks?status=completed", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "completed"

def test_get_task(setup_test_db):
    """Тест получения информации о задаче"""
    response = client.get("/api/tasks/task_1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "task_1"
    assert data["status"] == "completed"
    assert data["duration_seconds"] == 1800

def test_get_nonexistent_task(setup_test_db):
    """Тест получения несуществующей задачи"""
    response = client.get("/api/tasks/nonexistent", headers=headers)
    assert response.status_code == 404

def test_get_stats(setup_test_db):
    """Тест получения статистики"""
    response = client.get("/api/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_projects"] == 1
    assert data["total_tasks"] == 2
    assert data["active_tasks"] == 1
    assert data["completed_tasks"] == 1
    assert data["failed_tasks"] == 0

def test_webhook_endpoints_exist():
    """Проверка существования вебхук эндпоинтов"""
    endpoints = [
        "/webhook/start",
        "/webhook/finish",
        "/webhook/status",
        "/webhook/error"
    ]

    for endpoint in endpoints:
        response = client.post(endpoint, json={}, headers={"X-API-Key": "test"})
        assert response.status_code in [422, 401]  # Ожидаются ошибки валидации или авторизации

def test_api_without_db():
    """Тест API без подключения к базе данных"""
    # Очищаем переопределение зависимости
    app.dependency_overrides.clear()

    response = client.get("/api/projects", headers=headers)
    assert response.status_code == 500  # Ошибка из-за отсутствия DB