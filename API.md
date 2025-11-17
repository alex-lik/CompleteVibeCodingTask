# API Documentation

## Overview

Agent Task Tracker предоставляет RESTful API и WebSocket интерфейсы для интеграции с AI-агентами и фронтенд приложениями.

**Base URL:** `http://localhost:8000`
**API Documentation:** `http://localhost:8000/docs` (Swagger UI)
**Alternative Documentation:** `http://localhost:8000/redoc` (ReDoc)

## Авторизация

Все API эндпоинты требуют авторизации через API ключ.

### Способы авторизации

1. **HTTP Header** (рекомендуется):
   ```
   X-API-Key: <your-api-key>
   ```

2. **Query параметр**:
   ```
   ?api_key=<your-api-key>
   ```

3. **WebSocket query параметр**:
   ```
   ws://localhost:8000/ws?api_key=<your-api-key>&project=<project-name>
   ```

### Настройка API ключа

```bash
# В файле .env
API_KEY=your-secure-api-key
SECRET_KEY=your-secure-secret-key
```

## Вебхук эндпоинты

Эндпоинты для получения уведомлений от AI-агентов о статусе выполнения задач.

### POST /webhook/start
Начало выполнения задачи.

**Request:**
```json
{
  "project": "my-project",
  "task": "Разработка новой фичи",
  "task_id": "task-123",
  "agent": "claude-3-5-sonnet",
  "metadata": {
    "priority": "high",
    "estimated_duration": 3600,
    "dependencies": ["task-100", "task-101"]
  }
}
```

**Response:**
```json
{
  "status": "started",
  "task_id": "task-123",
  "message": "Task started successfully",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

### POST /webhook/finish
Завершение выполнения задачи.

**Request:**
```json
{
  "project": "my-project",
  "task": "Разработка новой фичи",
  "task_id": "task-123",
  "agent": "claude-3-5-sonnet",
  "result": "Feature successfully implemented with all tests passing",
  "duration_seconds": 3450,
  "metadata": {
    "files_created": ["feature.py", "test_feature.py"],
    "lines_of_code": 250,
    "test_coverage": 95
  }
}
```

**Response:**
```json
{
  "status": "completed",
  "task_id": "task-123",
  "message": "Task completed successfully",
  "duration_seconds": 3450,
  "timestamp": "2024-01-15T11:00:00Z"
}
```

### POST /webhook/status
Обновление статуса выполнения задачи.

**Request:**
```json
{
  "project": "my-project",
  "task": "Разработка новой фичи",
  "task_id": "task-123",
  "agent": "claude-3-5-sonnet",
  "status": "running",
  "progress": 75,
  "message": "Implementing core functionality, 75% complete"
}
```

**Response:**
```json
{
  "status": "updated",
  "task_id": "task-123",
  "message": "Task status updated successfully",
  "timestamp": "2024-01-15T10:45:00Z"
}
```

### POST /webhook/error
Сообщения об ошибках выполнения.

**Request:**
```json
{
  "project": "my-project",
  "task": "Разработка новой фичи",
  "task_id": "task-123",
  "agent": "claude-3-5-sonnet",
  "error_type": "RuntimeError",
  "error_message": "Failed to connect to database",
  "stack_trace": "Traceback (most recent call last):\n  File \"main.py\", line 42\n    db.connect()\nRuntimeError: Failed to connect to database",
  "metadata": {
    "retry_count": 3,
    "error_code": "DB_CONN_ERROR"
  }
}
```

**Response:**
```json
{
  "status": "error_recorded",
  "task_id": "task-123",
  "message": "Error recorded successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## REST API эндпоинты

Эндпоинты для фронтенда и интеграции с другими системами.

### GET /api/projects
Получение списка всех проектов.

**Parameters:**
- `limit` (optional): Количество проектов на странице (default: 50)
- `offset` (optional): Смещение для пагинации (default: 0)
- `sort_by` (optional): Поле сортировки (name, created_at, updated_at)
- `sort_order` (optional): Порядок сортировки (asc, desc)

**Response:**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "my-project",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z",
      "task_count": 15,
      "active_tasks": 3
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### GET /api/projects/{project_name}/tasks
Получение задач конкретного проекта.

**Parameters:**
- `project_name` (path): Имя проекта
- `limit` (optional): Количество задач на странице (default: 20)
- `offset` (optional): Смещение для пагинации (default: 0)
- `status` (optional): Фильтр по статусу (pending, running, completed, failed)
- `agent` (optional): Фильтр по агенту
- `date_from` (optional): Фильтр по дате начала
- `date_to` (optional): Фильтр по дате окончания

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "task_id": "task-123",
      "title": "Разработка новой фичи",
      "status": "completed",
      "progress": 100,
      "agent": "claude-3-5-sonnet",
      "started_at": "2024-01-15T10:00:00Z",
      "finished_at": "2024-01-15T11:00:00Z",
      "duration_seconds": 3600,
      "result": "Feature successfully implemented",
      "metadata": {
        "files_created": ["feature.py"],
        "lines_of_code": 250
      }
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0,
  "filters": {
    "status": "completed"
  }
}
```

### GET /api/stats
Получение общей статистики.

**Response:**
```json
{
  "overview": {
    "total_projects": 5,
    "total_tasks": 42,
    "active_tasks": 3,
    "completed_tasks": 35,
    "failed_tasks": 4
  },
  "performance": {
    "average_duration": 2450.5,
    "success_rate": 87.5,
    "total_duration": 102900
  },
  "agents": [
    {
      "name": "claude-3-5-sonnet",
      "task_count": 25,
      "success_rate": 92.0,
      "average_duration": 2100
    }
  ],
  "recent_activity": [
    {
      "project": "my-project",
      "task_id": "task-124",
      "status": "completed",
      "timestamp": "2024-01-15T12:00:00Z"
    }
  ]
}
```

### GET /api/stats/projects/{project_name}
Получение статистики по конкретному проекту.

**Response:**
```json
{
  "project": "my-project",
  "task_stats": {
    "total": 15,
    "completed": 12,
    "running": 2,
    "failed": 1
  },
  "performance": {
    "average_duration": 1800,
    "success_rate": 80.0
  },
  "timeline": [
    {
      "date": "2024-01-15",
      "completed": 3,
      "failed": 0
    }
  ]
}
```

## WebSocket API

### WebSocket эндпоинт
`ws://localhost:8000/ws?api_key=<your-api-key>&project=<project-name>`

### Типы сообщений

#### task_started
```json
{
  "type": "task_started",
  "data": {
    "task_id": "task-123",
    "title": "Разработка новой фичи",
    "project": "my-project",
    "agent": "claude-3-5-sonnet",
    "status": "running",
    "started_at": "2024-01-15T10:00:00Z"
  },
  "timestamp": "2024-01-15T10:00:00Z"
}
```

#### task_status_updated
```json
{
  "type": "task_status_updated",
  "data": {
    "task_id": "task-123",
    "project": "my-project",
    "status": "running",
    "progress": 75,
    "message": "Implementing core functionality"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### task_finished
```json
{
  "type": "task_finished",
  "data": {
    "task_id": "task-123",
    "title": "Разработка новой фичи",
    "project": "my-project",
    "agent": "claude-3-5-sonnet",
    "status": "completed",
    "duration_seconds": 3600,
    "result": "Feature successfully implemented"
  },
  "timestamp": "2024-01-15T11:00:00Z"
}
```

#### task_error
```json
{
  "type": "task_error",
  "data": {
    "task_id": "task-123",
    "title": "Разработка новой фичи",
    "project": "my-project",
    "agent": "claude-3-5-sonnet",
    "status": "failed",
    "error_type": "RuntimeError",
    "error_message": "Failed to connect to database"
  },
  "timestamp": "2024-01-15T10:45:00Z"
}
```

## Health Check эндпоинты

### GET /health
Проверка здоровья приложения.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00Z",
  "version": "1.0.0"
}
```

### GET /db-check
Проверка подключения к базе данных.

**Response:**
```json
{
  "status": "connected",
  "database": "postgresql",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

### GET /redis-check
Проверка подключения к Redis.

**Response:**
```json
{
  "status": "connected",
  "redis_version": "7.0.0",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

## WebSocket Статистика

### GET /api/websocket/stats
Получение статистики WebSocket подключений.

**Response:**
```json
{
  "total_connections": 5,
  "project_connections": {
    "my-project": 3,
    "another-project": 2
  },
  "uptime": 86400,
  "messages_sent": 150,
  "messages_received": 25
}
```

## Ограничения и безопасность

### Rate Limiting
- Webhook эндпоинты: 100 запросов в минуту
- REST API: 1000 запросов в минуту
- WebSocket подключения: 10 одновременных подключений на проект

### Размер запросов
- Максимальный размер JSON: 1MB
- Максимальный размер stack_trace: 10KB

### Безопасность
- Все эндпоинты требуют валидный API ключ
- CORS настроен для доменов фронтенда
- Валидация всех входных данных через Pydantic
- SQL injection защита через SQLAlchemy

## Примеры использования

### Python клиент
```python
import requests

class AgentTaskTracker:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    def start_task(self, project, task, task_id, agent, metadata=None):
        data = {
            "project": project,
            "task": task,
            "task_id": task_id,
            "agent": agent,
            "metadata": metadata or {}
        }
        response = requests.post(
            f"{self.base_url}/webhook/start",
            headers=self.headers,
            json=data
        )
        return response.json()

    def finish_task(self, project, task, task_id, agent, result, duration, metadata=None):
        data = {
            "project": project,
            "task": task,
            "task_id": task_id,
            "agent": agent,
            "result": result,
            "duration_seconds": duration,
            "metadata": metadata or {}
        }
        response = requests.post(
            f"{self.base_url}/webhook/finish",
            headers=self.headers,
            json=data
        )
        return response.json()

# Использование
tracker = AgentTaskTracker("http://localhost:8000", "your-api-key")
tracker.start_task("my-project", "Test task", "task-001", "test-agent")
```

### JavaScript клиент с WebSocket
```javascript
class TaskTrackerClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
        this.ws = null;
    }

    connect(projectName) {
        const wsUrl = `${this.baseUrl.replace('http', 'ws')}/ws?api_key=${this.apiKey}&project=${projectName}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received:', data);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
        };
    }

    async getProjects() {
        const response = await fetch(`${this.baseUrl}/api/projects`, {
            headers: { 'X-API-Key': this.apiKey }
        });
        return response.json();
    }
}

// Использование
const client = new TaskTrackerClient('http://localhost:8000', 'your-api-key');
client.connect('my-project');
```

## Ошибки

### Стандартные HTTP статусы
- `200 OK` - Успешное выполнение
- `201 Created` - Ресурс успешно создан
- `400 Bad Request` - Неверный формат запроса
- `401 Unauthorized` - Неверный API ключ
- `404 Not Found` - Ресурс не найден
- `422 Unprocessable Entity` - Ошибка валидации данных
- `429 Too Many Requests` - Превышен лимит запросов
- `500 Internal Server Error` - Внутренняя ошибка сервера

### Формат ошибки
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid data format",
    "details": {
      "field": "task_id",
      "issue": "This field is required"
    }
  },
  "timestamp": "2024-01-15T12:00:00Z"
}
```