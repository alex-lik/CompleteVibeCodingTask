# TODO — Полный чеклист разработки проекта

## Подготовка
- [x] Инициализировать репозиторий
- [x] Создать базовую структуру папок
- [x] Создать `.env.example` и `.gitignore`

## Backend — базовый функционал
- [x] Инициализировать FastAPI проект
- [x] Настроить подключение к PostgreSQL
- [x] Настроить Redis
- [x] Создать модели: Project, Task, Agent, Settings
- [x] Настроить Alembic и миграции
- [x] Эндпойнт `/webhook/start`
- [x] Эндпойнт `/webhook/finish`
- [x] Эндпойнт `/webhook/status`
- [ ] Эндпойнт `/webhook/error`
- [ ] API для фронтенда (список проектов, задач)
- [ ] Реализация WebSocket уведомлений
- [ ] Авторизация (API Key)

## Backend — расширенный функционал
- [ ] Пагинация и фильтры
- [ ] Сохранение настроек пользователя
- [ ] API статистики
- [ ] Тесты (pytest)

## MCP и скрипты
- [ ] Сделать MCP-адаптер
- [ ] Пример интеграции MCP
- [ ] Создать send_start.sh
- [ ] Создать send_finish.sh
- [ ] Версии для Windows (.bat)

## Frontend
- [ ] Инициализировать Vite + React
- [ ] Настроить Tailwind
- [ ] Установить shadcn/ui
- [ ] Реализовать WebSocket клиент
- [ ] Страница проектов
- [ ] Карточка проекта
- [ ] История задач
- [ ] Статистика
- [ ] Настройки темы

## Docker & Deployment
- [ ] Production Dockerfile backend
- [ ] Production Dockerfile frontend
- [ ] Docker Compose
- [ ] Health-checks

## CI/CD
- [ ] GitHub Actions pipeline
- [ ] Линтеры
- [ ] Unit + e2e тесты

## Документация
- [ ] README финальный
- [ ] API спецификация
- [ ] Agent Prompt
