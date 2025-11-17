# Agent Task Tracker

Полноценная система для приёма вебхуков от AI-агентов, отображения задач по проектам, ведения статистики и организации работы с несколькими проектами одновременно.

## Возможности
- Приём webhook: start / finish / status / error.
- REST API для получения проектов, задач и статистики с пагинацией и фильтрацией.
- WebSocket-уведомления в реальном времени с полноценным клиентом на React.
- Реактивный фронтенд на React + TypeScript + Vite + shadcn/ui.
- Расширенная система пагинации и фильтров для всех API эндпоинтов.
- Хранение данных: PostgreSQL + Redis.
- Контейнеризация Docker.
- **MCP (Model Context Protocol) адаптер** для удобной интеграции с AI-агентами.
- Скрипты для отправки вебхуков (Shell и Batch версии).
- Тестирование: pytest с покрытием 20+ тестами.

## Структура проекта
```
.
├─ backend/                    # FastAPI backend
│  ├─ webhook/                 # Вебхук эндпоинты
│  ├─ api/                     # REST API для фронтенда
│  ├─ mcp/                     # MCP адаптер для AI-агентов
│  ├─ core/                    # Конфигурация и подключения
│  ├─ models/                  # SQLAlchemy модели и Pydantic схемы
│  ├─ services/               # Сервисная логика
│  ├─ alembic/                 # Миграции БД
│  ├─ tests/                   # Тесты
│  ├─ requirements.txt         # Зависимости Python
│  └─ Dockerfile              # Production Docker конфигурация
├─ frontend/                   # React фронтенд
│  ├─ src/                     # Исходный код
│  ├─ public/                  # Статические файлы
│  ├─ package.json             # Зависимости Node.js
│  ├─ Dockerfile              # Production Docker конфигурация
│  └─ nginx.conf              # Конфигурация nginx
├─ nginx/                      # Nginx reverse proxy конфигурация
│  └─ nginx.conf              # Основная конфигурация
├─ .github/workflows/          # GitHub Actions CI/CD
│  ├─ ci.yml                  # Основной CI/CD pipeline
│  ├─ lint.yml                # Линтинг и качество кода
│  └─ e2e.yml                 # E2E тестирование
├─ infra/
│  └─ docker-compose.yml      # Development Docker конфигурация
├─ scripts/                   # Скрипты для агентов
├─ docker-compose.yml         # Production Docker конфигурация
├─ .env.production.example     # Production переменные окружения
├─ DEPLOYMENT.md              # Инструкция по развертыванию
├─ CHANGELOG.md               # Журнал изменений
├─ TODO.md                    # Чеклист задач
└─ README.md                  # Основная документация
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

#### Development
```bash
# Development с volume монтированием
docker-compose -f infra/docker-compose.yml up --build
```

#### Production
```bash
# Production развертывание
cp .env.production.example .env
# Отредактировать .env с вашими production значениями
docker-compose up --build -d
```

### 4. Production развертывание

Полная инструкция по развертыванию в production описана в [DEPLOYMENT.md](./DEPLOYMENT.md).

**Краткая инструкция:**
```bash
# 1. Клонировать и настроить
git clone <repository-url>
cd CompleteVibeCodingTask
cp .env.production.example .env
# Настроить переменные окружения

# 2. Развернуть
docker-compose up -d

# 3. Инициализировать БД (первый раз)
docker-compose exec backend alembic upgrade head
```

### 4. Локальная разработка

#### Backend
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
# Сервер запустится на http://localhost:8002
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
# Фронтенд запустится на http://localhost:3000
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

## CI/CD и Качество кода

### GitHub Actions
Проект включает полноценный CI/CD pipeline:

- **Основной pipeline** (`.github/workflows/ci.yml`):
  - Тестирование backend с покрытием
  - Сборка и тестирование frontend
  - Сканер безопасности (Trivy)
  - Сборка и публикация Docker образов
  - Автоматический деплой в production

- **Линтинг и качество** (`.github/workflows/lint.yml`):
  - Python: ruff, black, isort, mypy
  - Frontend: ESLint, Prettier, TypeScript
  - Безопасность: Bandit

- **E2E тестирование** (`.github/workflows/e2e.yml`):
  - Полное тестирование вебхуков
  - E2E тесты frontend (Playwright)
  - Нагрузочное тестирование (Locust)

### Локальное тестирование

#### Backend
```bash
cd backend
python -m pytest tests/ -v --cov=. --cov-report=html

# Линтинг
ruff check .
black --check .
isort --check-only .
mypy .
```

#### Frontend
```bash
cd frontend
npm run lint
npm run type-check
npm run build

# Форматирование
npm run format:check
npm run format
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

Система поддерживает WebSocket уведомления в реальном времени о событиях задач с полноценным клиентом.

### Подключение к WebSocket
```javascript
// Подключение к WebSocket
const ws = new WebSocket('ws://localhost:8000/webhook/ws?project=my-project');

// Прослушивание сообщений
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### React WebSocket клиент

**Автоматически управляемый WebSocket хук:**
```typescript
import { useWebSocket } from './hooks/useWebSocket';

function MyComponent() {
  const { connectionState, isConnected, sendMessage } = useWebSocket({
    projectName: 'my-project',
    enableNotifications: true,
    onConnect: () => console.log('Connected!'),
    onDisconnect: () => console.log('Disconnected!'),
  });

  return (
    <div>
      <p>Статус: {connectionState.status}</p>
      {isConnected && <p>🟢 Подключено</p>}
    </div>
  );
}
```

**Возможности WebSocket клиента:**
- ✅ Автоматическое переподключение (5 попыток)
- ✅ Ping/Pong для поддержания соединения
- ✅ Обработка всех типов сообщений
- ✅ Уведомления через react-hot-toast
- ✅ Глобальный контекст для всего приложения
- ✅ Индикатор статуса в UI
- ✅ Отладочная панель с историей сообщений

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

✅ **Полностью выполнено:**
- Backend: FastAPI + SQLAlchemy + PostgreSQL + Redis
- Вебхук эндпоинты: start, finish, status, error
- REST API для фронтенда с пагинацией и фильтрами
- Модели: Project, Task, Agent, Settings
- Миграции базы данных (Alembic)
- Тестирование API (20+ тестов)
- WebSocket уведомления в реальном времени
- **Полноценный React фронтенд с TypeScript + shadcn/ui**
- **WebSocket клиент с автоматическим переподключением**
- **Интеграция с react-hot-toast для уведомлений**
- MCP адаптер для AI-агентов
- Скрипты для отправки вебхуков (Shell/Batch)
- **Production Docker конфигурация (backend + frontend)**
- **Nginx reverse proxy с SSL поддержкой**
- **Полноценный CI/CD pipeline (GitHub Actions)**
- **Линтинг и качество кода**
- **E2E тестирование**
- **Health checks и мониторинг**
- **Production-ready документация**

🎯 **Проект готов к production развертыванию!**

## Архитектура и технологии

### Backend
- **FastAPI** - современный веб-фреймворк
- **PostgreSQL** - основная база данных
- **Redis** - кэширование и сессии
- **SQLAlchemy** - ORM
- **Alembic** - миграции БД
- **Pydantic** - валидация данных
- **Pytest** - тестирование
- **WebSocket** - real-time уведомления

### Frontend
- **React 18** с TypeScript
- **Vite** - быструя сборка
- **Tailwind CSS** - стилизация
- **shadcn/ui** - компоненты
- **React Router** - навигация
- **React Query** - управление состоянием
- **react-hot-toast** - уведомления

### DevOps
- **Docker** - контейнеризация
- **Nginx** - reverse proxy
- **GitHub Actions** - CI/CD
- **Codecov** - покрытие тестов
- **Trivy** - сканер безопасности
