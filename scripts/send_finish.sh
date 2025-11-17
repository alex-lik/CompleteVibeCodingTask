#!/bin/bash

# send_finish.sh - Скрипт для отправки вебхука о завершении задачи
# Использование: ./send_finish.sh <project_name> <task_description> <agent_name> <result> [task_id] [duration_seconds] [api_key] [base_url]

set -e

# Параметры по умолчанию
DEFAULT_API_KEY="dev-api-key"
DEFAULT_BASE_URL="http://localhost:8001"
DEFAULT_TASK_ID="task-$(date +%s)"

# Проверка обязательных параметров
if [ $# -lt 4 ]; then
    echo "Использование: $0 <project_name> <task_description> <agent_name> <result> [task_id] [duration_seconds] [api_key] [base_url]"
    echo ""
    echo "Параметры:"
    echo "  project_name     - Название проекта"
    echo "  task_description - Описание задачи"
    echo "  agent_name       - Имя агента"
    echo "  result           - Результат выполнения задачи"
    echo "  task_id          - ID задачи (опционально)"
    echo "  duration_seconds - Длительность выполнения в секундах (опционально)"
    echo "  api_key          - API ключ (опционально, по умолчанию: $DEFAULT_API_KEY)"
    echo "  base_url         - Base URL API (опционально, по умолчанию: $DEFAULT_BASE_URL)"
    echo ""
    echo "Примеры:"
    echo "  $0 my-project 'Разработка API' claude-3-5 'API разработан успешно'"
    echo "  $0 my-project 'Разработка API' claude-3-5 'API разработан успешно' task-123 300"
    echo "  $0 my-project 'Разработка API' claude-3-5 'API разработан успешно' task-123 300 my-api-key http://localhost:8001"
    exit 1
fi

# Получение параметров
PROJECT_NAME="$1"
TASK_DESCRIPTION="$2"
AGENT_NAME="$3"
RESULT="$4"
TASK_ID="${5:-$DEFAULT_TASK_ID}"
DURATION_SECONDS="$6"
API_KEY="${7:-$DEFAULT_API_KEY}"
BASE_URL="${8:-$DEFAULT_BASE_URL}"

# Формирование URL
WEBHOOK_URL="$BASE_URL/webhook/finish"

# Создание JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
    "project": "$PROJECT_NAME",
    "task": "$TASK_DESCRIPTION",
    "task_id": "$TASK_ID",
    "agent": "$AGENT_NAME",
    "result": "$RESULT",
    "metadata": {
        "script": "send_finish.sh",
        "timestamp": "$(date -Iseconds)",
        "hostname": "$(hostname)",
        "user": "$(whoami)"
    }
EOF
)

# Добавляем duration_seconds если указан
if [ -n "$DURATION_SECONDS" ]; then
    JSON_PAYLOAD="$JSON_PAYLOAD,$(cat <<EOF

    "duration_seconds": $DURATION_SECONDS
EOF
)"
fi

JSON_PAYLOAD="$JSON_PAYLOAD$(cat <<EOF

}
EOF
)"

echo "🎉 Отправка вебхука о завершении задачи..."
echo "Проект: $PROJECT_NAME"
echo "Задача: $TASK_DESCRIPTION"
echo "Агент: $AGENT_NAME"
echo "Task ID: $TASK_ID"
echo "Результат: $RESULT"
[ -n "$DURATION_SECONDS" ] && echo "Длительность: $DURATION_SECONDS секунд"
echo "URL: $WEBHOOK_URL"
echo ""

# Отправка запроса
HTTP_STATUS=$(curl -s -o /tmp/webhook_response.json -w "%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "$JSON_PAYLOAD" \
    "$WEBHOOK_URL")

# Проверка результата
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Вебхук успешно отправлен!"
    echo "Ответ сервера:"
    cat /tmp/webhook_response.json | python3 -m json.tool 2>/dev/null || cat /tmp/webhook_response.json
else
    echo "❌ Ошибка при отправке вебхука!"
    echo "HTTP статус: $HTTP_STATUS"
    echo "Ответ сервера:"
    cat /tmp/webhook_response.json
    exit 1
fi

# Очистка временного файла
rm -f /tmp/webhook_response.json

echo ""
echo "📋 Детали задачи:"
echo "Task ID: $TASK_ID"
echo "Project: $PROJECT_NAME"
echo "Agent: $AGENT_NAME"
echo "Статус: ✅ Завершена"