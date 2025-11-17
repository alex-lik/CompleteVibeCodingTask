@echo off
REM send_start.bat - Скрипт для отправки вебхука о начале задачи (Windows)
REM Использование: send_start.bat <project_name> <task_description> <agent_name> [task_id] [api_key] [base_url]

setlocal enabledelayedexpansion

REM Параметры по умолчанию
set "DEFAULT_API_KEY=dev-api-key"
set "DEFAULT_BASE_URL=http://localhost:8001"

REM Проверка обязательных параметров
if "%~3"=="" (
    echo Использование: %~nx0 ^<project_name^> ^<task_description^> ^<agent_name^> [task_id] [api_key] [base_url]
    echo.
    echo Параметры:
    echo   project_name     - Название проекта
    echo   task_description - Описание задачи
    echo   agent_name       - Имя агента
    echo   task_id          - ID задачи (опционально)
    echo   api_key          - API ключ (опционально, по умолчанию: %DEFAULT_API_KEY%)
    echo   base_url         - Base URL API (опционально, по умолчанию: %DEFAULT_BASE_URL%)
    echo.
    echo Пример:
    echo   %~nx0 my-project "Разработка API" claude-3-5
    echo   %~nx0 my-project "Разработка API" claude-3-5 custom-task-123 my-api-key http://localhost:8001
    exit /b 1
)

REM Получение параметров
set "PROJECT_NAME=%~1"
set "TASK_DESCRIPTION=%~2"
set "AGENT_NAME=%~3"

REM Генерация task_id по умолчанию на основе времени
for /f "tokens=1-6 delims= " %%a in ("%date% %time%") do (
    set "TIMESTAMP=%%a%%b%%c%%d%%e%%f"
)
set "TIMESTAMP=!TIMESTAMP:/=!"
set "TIMESTAMP=!TIMESTAMP::=!"
set "TIMESTAMP=!TIMESTAMP:.=!"
set "DEFAULT_TASK_ID=task-!TIMESTAMP!"

set "TASK_ID=%~4"
if "%TASK_ID%"=="" set "TASK_ID=%DEFAULT_TASK_ID%"

set "API_KEY=%~5"
if "%API_KEY%"=="" set "API_KEY=%DEFAULT_API_KEY%"

set "BASE_URL=%~6"
if "%BASE_URL%"=="" set "BASE_URL=%DEFAULT_BASE_URL%"

REM Формирование URL
set "WEBHOOK_URL=%BASE_URL%/webhook/start"

REM Создание временного JSON файла
set "JSON_FILE=%TEMP%\webhook_start_%RANDOM%.json"

REM Создание JSON payload
(
echo {
echo     "project": "%PROJECT_NAME%",
echo     "task": "%TASK_DESCRIPTION%",
echo     "task_id": "%TASK_ID%",
echo     "agent": "%AGENT_NAME%",
echo     "metadata": {
echo         "script": "send_start.bat",
echo         "timestamp": "%date% %time%",
echo         "hostname": "%COMPUTERNAME%",
echo         "user": "%USERNAME%"
echo     }
echo }
) > "%JSON_FILE%"

echo 🚀 Отправка вебхука о начале задачи...
echo Проект: %PROJECT_NAME%
echo Задача: %TASK_DESCRIPTION%
echo Агент: %AGENT_NAME%
echo Task ID: %TASK_ID%
echo URL: %WEBHOOK_URL%
echo.

REM Отправка запроса с использованием curl
curl -s -o "%TEMP%\webhook_response.json" -w "%%{http_code}" ^
    -X POST ^
    -H "Content-Type: application/json" ^
    -H "X-API-Key: %API_KEY%" ^
    -d @"%JSON_FILE%" ^
    "%WEBHOOK_URL%" > "%TEMP%\http_status.txt"

REM Читаем HTTP статус
set /p HTTP_STATUS=<"%TEMP%\http_status.txt"

REM Проверка результата
if "%HTTP_STATUS%"=="200" (
    echo ✅ Вебхук успешно отправлен!
    echo Ответ сервера:
    if exist "%TEMP%\webhook_response.json" (
        type "%TEMP%\webhook_response.json"
    )
) else (
    echo ❌ Ошибка при отправке вебхука!
    echo HTTP статус: %HTTP_STATUS%
    echo Ответ сервера:
    if exist "%TEMP%\webhook_response.json" (
        type "%TEMP%\webhook_response.json"
    )
    del "%JSON_FILE%" 2>nul
    del "%TEMP%\webhook_response.json" 2>nul
    del "%TEMP%\http_status.txt" 2>nul
    exit /b 1
)

REM Очистка временных файлов
del "%JSON_FILE%" 2>nul
del "%TEMP%\webhook_response.json" 2>nul
del "%TEMP%\http_status.txt" 2>nul

echo.
echo 📋 Детали задачи для дальнейшего использования:
echo Task ID: %TASK_ID%
echo Project: %PROJECT_NAME%
echo Agent: %AGENT_NAME%

endlocal