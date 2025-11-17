# MCP и Скрипты для Вебхуков

## MCP (Model Context Protocol) Адаптер

MCP адаптер предоставляет удобный интерфейс для AI-агентов взаимодействия с системой отслеживания задач.

### Структура

```
backend/mcp/
├── __init__.py           # Основной MCP адаптер
├── examples.py          # Примеры использования
└── README.md            # Документация
```

### Основные компоненты

#### MCPAdapter

Основной класс для работы с API системы:

```python
from mcp import MCPAdapter

async with MCPAdapter() as mcp:
    # Начать задачу
    await mcp.start_task(
        project="my-project",
        task="Разработка фичи",
        task_id="task-123",
        agent="claude-3-5"
    )

    # Обновить статус
    await mcp.update_status(
        project="my-project",
        task="",
        task_id="task-123",
        agent="claude-3-5",
        status="running",
        progress=50
    )

    # Завершить задачу
    await mcp.finish_task(
        project="my-project",
        task="",
        task_id="task-123",
        agent="claude-3-5",
        result="Фича разработана"
    )
```

#### MCPContextManager

Удобный контекстный менеджер для агентов:

```python
from mcp import create_mcp_context

async with create_mcp_context("my-agent", "my-project") as ctx:
    # Начать задачу
    task_id = await ctx.start_task("Анализ данных")

    # Обновить прогресс
    await ctx.update_progress(25, "Загрузка данных")
    await ctx.update_progress(50, "Обработка")
    await ctx.update_progress(75, "Анализ")

    # Завершить задачу
    await ctx.complete_task("Анализ завершен")
```

---

## Скрипты для Вебхуков

Скрипты позволяют легко отправлять вебхуки из командной строки или других систем.

### Shell скрипты (Linux/macOS)

#### send_start.sh

Отправляет вебхук о начале задачи:

```bash
# Базовое использование
./send_start.sh my-project "Разработка API" claude-3-5

# Полное использование
./send_start.sh my-project "Разработка API" claude-3-5 task-123 my-api-key http://localhost:8001
```

#### send_finish.sh

Отправляет вебхук о завершении задачи:

```bash
# Базовое использование
./send_finish.sh my-project "Разработка API" claude-3-5 "API разработан успешно"

# С указанием длительности
./send_finish.sh my-project "Разработка API" claude-3-5 "API разработан успешно" task-123 300

# Полное использование
./send_finish.sh my-project "Разработка API" claude-3-5 "API разработан успешно" task-123 300 my-api-key http://localhost:8001
```

### Batch скрипты (Windows)

#### send_start.bat

```cmd
REM Базовое использование
send_start.bat my-project "Разработка API" claude-3-5

REM Полное использование
send_start.bat my-project "Разработка API" claude-3-5 task-123 my-api-key http://localhost:8001
```

#### send_finish.bat

```cmd
REM Базовое использование
send_finish.bat my-project "Разработка API" claude-3-5 "API разработан успешно"

REM С указанием длительности
send_finish.bat my-project "Разработка API" claude-3-5 "API разработан успешно" task-123 300

REM Полное использование
send_finish.bat my-project "Разработка API" claude-3-5 "API разработан успешно" task-123 300 my-api-key http://localhost:8001
```

---

## Примеры использования

### 1. Python агент с MCP

```python
#!/usr/bin/env python3
import asyncio
from mcp import create_mcp_context

async def data_processing_agent():
    async with create_mcp_context("data-processor", "data-analysis") as ctx:
        # Начинаем задачу
        task_id = await ctx.start_task(
            "Обработка данных клиента",
            metadata={"dataset": "customers.csv"}
        )

        try:
            # Имитация работы
            await ctx.update_progress(25, "Загрузка данных")
            await process_data()  # Ваша функция

            await ctx.update_progress(75, "Генерация отчета")
            report = generate_report()  # Ваша функция

            # Завершаем задачу
            await ctx.complete_task(
                "Обработка завершена",
                metadata={"report_path": report}
            )

        except Exception as e:
            await ctx.fail_task("ProcessingError", str(e))
            raise

if __name__ == "__main__":
    asyncio.run(data_processing_agent())
```

### 2. Интеграция с CI/CD

```bash
#!/bin/bash
# ci_pipeline.sh

PROJECT_NAME="frontend-build"
AGENT_NAME="github-actions"

# Начинаем сборку
./send_start.sh "$PROJECT_NAME" "Сборка фронтенда" "$AGENT_NAME"

# Выполняем сборку
if npm run build; then
    # Успешная сборка
    ./send_finish.sh "$PROJECT_NAME" "Сборка фронтенда" "$AGENT_NAME" "Сборка успешна" "" 120
else
    # Ошибка сборки
    curl -X POST "http://localhost:8001/webhook/error" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: dev-api-key" \
        -d '{
            "project": "'"$PROJECT_NAME"'",
            "task": "Сборка фронтенда",
            "task_id": "build-'$(date +%s)'",
            "agent": "'"$AGENT_NAME"'",
            "error_type": "BuildError",
            "error_message": "npm build failed"
        }'
    exit 1
fi
```

---

## Установка и настройка

### Требования

- Python 3.8+
- curl (для скриптов)
- Доступ к API серверу

### Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### Настройка

Скопируйте `.env.example` в `.env` и настройте:

```bash
cp .env.example .env
```

Основные параметры:

```env
# API настройки
BASE_URL=http://localhost:8001
API_KEY=your-secret-api-key

# Database
DATABASE_URL=postgresql://user:password@localhost/agent_tracker

# Redis
REDIS_URL=redis://localhost:6379/0
```

---

## Тестирование

Запуск тестов MCP адаптера:

```bash
cd backend
python -m pytest tests/test_mcp.py -v
```

Запуск примеров:

```bash
cd backend
python mcp/examples.py
```

Тестирование скриптов:

```bash
# Тестирование shell скриптов
./send_start.sh test-project "Test task" test-agent
./send_finish.sh test-project "Test task" test-agent "Test result"

# Тестирование batch скриптов (Windows)
send_start.bat test-project "Test task" test-agent
send_finish.bat test-project "Test task" test-agent "Test result"
```

---

## API Эндпоинты

### Вебхуки

- `POST /webhook/start` - Начать задачу
- `POST /webhook/finish` - Завершить задачу
- `POST /webhook/status` - Обновить статус
- `POST /webhook/error` - Сообщить об ошибке

### REST API

- `GET /api/projects` - Получить проекты
- `GET /api/projects/{name}/tasks` - Получить задачи проекта
- `GET /api/stats` - Получить статистику

### WebSocket

- `WS /webhook/ws?api_key={key}&project={name}` - Уведомления в реальном времени

---

## Логирование

MCP адаптер использует стандартный модуль `logging`:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Включить debug логирование
logging.getLogger('mcp').setLevel(logging.DEBUG)
```
