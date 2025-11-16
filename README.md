# Agent Task Tracker

Полноценная система для приёма вебхуков от AI-агентов, отображения задач по проектам, ведения статистики и организации работы с несколькими проектами одновременно.

## Возможности
- Приём webhook: start / finish / status / error.
- Реальное время: WebSocket-уведомления.
- UI: shadcn + Tailwind, карточки проектов, статистика.
- MCP и bash/bat скрипты для агентов.
- Полная контейнеризация Docker.
- Хранение данных: PostgreSQL + Redis.

## Структура проекта
```
.
├─ backend/
│  ├─ webhook/          # Вебхук эндпоинты
│  ├─ api/              # REST API
│  ├─ mcp/              # MCP адаптеры
│  ├─ models/           # SQLAlchemy модели
│  ├─ alembic/          # Миграции БД
│  ├─ requirements.txt  # Зависимости Python
│  └─ README.md         # Документация backend
├─ frontend/
│  ├─ src/              # React компоненты
│  ├─ package.json      # Зависимости Node.js
│  └─ README.md         # Документация frontend
├─ infra/
│  ├─ docker-compose.yml # Docker конфигурация
│  └─ README.md         # Документация инфраструктуры
├─ scripts/
│  ├─ send_start.sh     # Скрипт отправки start webhook
│  ├─ send_finish.sh    # Скрипт отправки finish webhook
│  └─ README.md         # Документация скриптов
├─ .env.example         # Пример переменных окружения
├─ CHANGELOG.md         # Журнал изменений
├─ TODO.md              # Чеклист задач
└─ README.md            # Основная документация
```

## Установка
1. Скопировать репозиторий
2. Создать `.env`
3. Запустить:
```
docker-compose up --build
```

## Тестовый webhook
```
curl -X POST http://localhost:8000/webhook/start   -H "Content-Type: application/json"   -d '{"project":"test","task":"Example","task_id":"task123","agent":"demo"}'
```

## Документация
Полная спецификация API — в Swagger по адресу `/docs`.
