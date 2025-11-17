# Agent Task Tracker

Полноценная система для приёма вебхуков от AI-агентов, отображения задач по проектам, ведения статистики и организации работы с несколькими проектами одновременно.

## Возможности
- Приём webhook: start / finish / status / error.
- REST API для получения проектов, задач и статистики.
- WebSocket-уведомления в реальном времени.
- Хранение данных: PostgreSQL + Redis.
- Контейнеризация Docker.
- Тестирование: pytest.

## Структура проекта
```
.
├─ backend/
│  ├─ webhook/          # Вебхук эндпоинты
│  ├─ api/              # REST API для фронтенда
│  ├─ core/             # Конфигурация и подключения
│  ├─ models/           # SQLAlchemy модели и Pydantic схемы
│  ├─ services/          # Сервисная логика
│  ├─ alembic/          # Миграции БД
│  ├─ tests/            # Тесты
│  ├─ requirements.txt  # Зависимости Python
│  └─ README.md         # Документация backend
├─ frontend/           # В разработке
├─ infra/
│  └─ docker-compose.yml # Docker конфигурация
├─ scripts/            # Скрипты для агентов
├─ .env.example        # Пример переменных окружения
├─ CHANGELOG.md        # Журнал изменений
├─ TODO.md             # Чеклист задач
└─ README.md            # Основная документация
```

## Быстрый старт

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd CompleteVibeCodingTask
```

### 2. Настройка окружения
```bash
# Создать файл окружения
cp .env.example .env

# Редактировать .env с вашими настройками
```

### 3. Запуск через Docker
```bash
docker-compose up --build
```

### 4. Локальная разработка backend
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```

## API Документация

### Авторизация

Все API эндпоинты требуют авторизации через API ключ.

**Заголовок авторизации:**
```
X-API-Key: <ваш-api-ключ>
```

**Настройка API ключа:**
```bash
# В файле .env
API_KEY=ваш-секретный-api-ключ
```

### Вебхук эндпоинты

#### Start Webhook
```bash
POST /webhook/start
Headers: X-API-Key: <your-api-key>
Content-Type: application/json

{
  "project": "my-project",
  "task": "Разработка фичи",
  "task_id": "task-123",
  "agent": "claude-3-5",
  "metadata": {"priority": "high"}
}
```

#### Finish Webhook
```bash
POST /webhook/finish
Headers: X-API-Key: <your-api-key>
Content-Type: application/json

{
  "project": "my-project",
  "task": "Разработка фичи",
  "task_id": "task-123",
  "agent": "claude-3-5",
  "result": "Завершено успешно",
  "duration_seconds": 1800,
  "metadata": {"files": ["result.py"]}
}
```

#### Status Webhook
```bash
POST /webhook/status
Headers: X-API-Key: <your-api-key>
Content-Type: application/json

{
  "project": "my-project",
  "task": "Разработка фичи",
  "task_id": "task-123",
  "agent": "claude-3-5",
  "status": "running",
  "progress": 75,
  "message": "Обработка данных"
}
```

#### Error Webhook
```bash
POST /webhook/error
Headers: X-API-Key: <your-api-key>
Content-Type: application/json

{
  "project": "my-project",
  "task": "Разработка фичи",
  "task_id": "task-123",
  "agent": "claude-3-5",
  "error_type": "RuntimeError",
  "error_message": "Ошибка выполнения",
  "stack_trace": "Traceback...",
  "metadata": {"attempt": 3}
}
```

### REST API эндпоинты

Все REST API эндпоинты требуют авторизации через заголовок `X-API-Key`.

#### Получить список проектов
```bash
GET /api/projects
Headers: X-API-Key: <your-api-key>
Response:
[
  {
    "id": 1,
    "name": "my-project",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
]
```

#### Получить задачи проекта
```bash
GET /api/projects/{project_name}/tasks?limit=10&offset=0&status=running
Response:
[
  {
    "id": 1,
    "task_id": "task-123",
    "title": "Разработка фичи",
    "status": "running",
    "progress": 75,
    "started_at": "2024-01-01T10:00:00Z"
  }
]
```

#### Получить статистику
```bash
GET /api/stats
Response:
{
  "total_projects": 5,
  "total_tasks": 42,
  "active_tasks": 3,
  "completed_tasks": 35,
  "failed_tasks": 4,
  "average_duration": 2450.5
}
```

#### Получить статистику WebSocket подключений
```bash
GET /api/websocket/stats
Headers: X-API-Key: <your-api-key>
Response:
{
  "total_connections": 3,
  "project_connections": {
    "my-project": 2,
    "another-project": 1
  }
}
```

### WebSocket уведомления

WebSocket эндпоинт также требует авторизации через query параметр:

```bash
ws://localhost:8000/webhook/ws?api_key=<your-api-key>&project=my-project
```

## Тестирование

### Запуск тестов
```bash
cd backend
python -m pytest tests/ -v
```

### Тестирование эндпоинтов
```bash
# Запустить базовые тесты
python -m pytest tests/test_api_basic.py -v

# Запустить все тесты
python -m pytest tests/ -v --tb=short
```

## Примеры интеграции

### Python
```python
import requests

# Запустить задачу
response = requests.post(
    "http://localhost:8000/webhook/start",
    headers={"X-API-Key": "your-api-key"},
    json={
        "project": "my-app",
        "task": "Обработка данных",
        "task_id": "python-task-123",
        "agent": "python-agent"
    }
)

# Обновить статус
response = requests.post(
    "http://localhost:8000/webhook/status",
    headers={"X-API-Key": "your-api-key"},
    json={
        "project": "my-app",
        "task": "Обработка данных",
        "task_id": "python-task-123",
        "agent": "python-agent",
        "status": "running",
        "progress": 50
    }
)
```

### cURL
```bash
# Запустить задачу
curl -X POST http://localhost:8000/webhook/start \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"project":"my-app","task":"Обработка данных","task_id":"curl-task-123","agent":"curl-agent"}'

# Обновить статус
curl -X POST http://localhost:8000/webhook/status \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"project":"my-app","task":"Обработка данных","task_id":"curl-task-123","agent":"curl-agent","status":"running","progress":50}'
```

## WebSocket API

Система поддерживает WebSocket уведомления в реальном времени о событиях задач.

### Подключение к WebSocket
```javascript
// Подключение к WebSocket
const ws = new WebSocket('ws://localhost:8000/webhook/ws?project=my-project');

// Прослушивание сообщений
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Примеры сообщений:
// Начало задачи
{
    "type": "task_started",
    "data": {
        "task_id": "task-123",
        "title": "Разработка фичи",
        "project": "my-project",
        "agent": "claude-3-5",
        "status": "running",
        "started_at": "2024-01-01T10:00:00Z"
    },
    "timestamp": "2024-01-01T10:00:00Z"
}

// Завершение задачи
{
    "type": "task_finished",
    "data": {
        "task_id": "task-123",
        "title": "Разработка фичи",
        "project": "my-project",
        "agent": "claude-3-5",
        "status": "completed",
        "duration_seconds": 1800,
        "finished_at": "2024-01-01T10:30:00Z"
    },
    "timestamp": "2024-01-01T10:30:00Z"
}

// Ошибка задачи
{
    "type": "task_error",
    "data": {
        "task_id": "task-123",
        "title": "Разработка фичи",
        "project": "my-project",
        "agent": "claude-3-5",
        "status": "failed",
        "error_type": "RuntimeError",
        "error_message": "Ошибка выполнения"
    },
    "timestamp": "2024-01-01T10:30:00Z"
}
```

## Документация

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
- **Примеры webhook**: См. раздел "Вебхук эндпоинты"
- **Детальное API**: См. раздел "REST API эндпоинты"
- **WebSocket статистика**: `/api/websocket/stats`

## Health Checks

```bash
# Проверка здоровья приложения
GET /health

# Проверка подключения к БД
GET /db-check

# Проверка подключения к Redis
GET /redis-check
```

## Статус разработки

✅ **Выполнено:**
- Backend: FastAPI + SQLAlchemy
- Вебхук эндпоинты: start, finish, status, error
- REST API для фронтенда
- Модели: Project, Task, Agent, Settings
- Миграции базы данных
- Тестирование API
- Базовая документация

🚧 **В разработке:**
- Frontend (React + shadcn/ui)
- Production Dockerfile
- CI/CD pipeline

📋 **Следующие задачи (по TODO.md):**
- API статистики
- Авторизация (API Key)
- Фронтенд интерфейс
