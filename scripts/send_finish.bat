@echo off
REM send_finish.bat - Скрипт для отправки вебхука о завершении задачи (Windows)
REM Использование: send_finish.bat <project_name> <task_description> <agent_name> <result> [task_id] [duration_seconds] [api_key] [base_url]

setlocal enabledelayedexpansion

REM Параметры по умолчанию
set "DEFAULT_API_KEY=dev-api-key"
set "DEFAULT_BASE_URL=http://localhost:8001"

REM Проверка обязательных параметров
if "%~4"=="" (
    echo Использование: %~nx0 ^<project_name^> ^<task_description^> ^<agent_name^> ^<result^> [task_id] [duration_seconds] [api_key] [base_url]
    echo.
    echo Параметры:
    echo   project_name     - Название проекта
    echo   task_description - Описание задачи
    echo   agent_name       - Имя агента
    echo   result           - Результат выполнения задачи
    echo   task_id          - ID задачи (опционально)
    echo   duration_seconds - Длительность выполнения в секундах (опционально)
    echo   api_key          - API ключ (опционально, по умолчанию: %DEFAULT_API_KEY%)
    echo   base_url         - Base URL API (опционально, по умолчанию: %DEFAULT_BASE_URL%)
    echo.
    echo Примеры:
    echo   %~nx0 my-project "Разработка API" claude-3-5 "API разработан успешно"
    echo   %~nx0 my-project "Разработка API" claude-3-5 "API разработан успешно" task-123 300
    echo   %~nx0 my-project "Разработка API" claude-3-5 "API разработан успешно" task-123 300 my-api-key http://localhost:8001
    exit /b 1
)

REM Получение параметров
set "PROJECT_NAME=%~1"
set "TASK_DESCRIPTION=%~2"
set "AGENT_NAME=%~3"
set "RESULT=%~4"

REM Генерация task_id по умолчанию на основе времени
for /f "tokens=1-6 delims= " %%a in ("%date% %time%") do (
    set "TIMESTAMP=%%a%%b%%c%%d%%e%%f"
)
set "TIMESTAMP=!TIMESTAMP:/=!"
set "TIMESTAMP=!TIMESTAMP::=!"
set "TIMESTAMP=!TIMESTAMP:.=!"
set "DEFAULT_TASK_ID=task-!TIMESTAMP!"

set "TASK_ID=%~5"
if "%TASK_ID%"=="" set "TASK_ID=%DEFAULT_TASK_ID%"

set "DURATION_SECONDS=%~6"
set "API_KEY=%~7"
if "%API_KEY%"=="" set "API_KEY=%DEFAULT_API_KEY%"

set "BASE_URL=%~8"
if "%BASE_URL%"=="" set "BASE_URL=%DEFAULT_BASE_URL%"

REM Формирование URL
set "WEBHOOK_URL=%BASE_URL%/webhook/finish"

REM Создание временного JSON файла
set "JSON_FILE=%TEMP%\webhook_finish_%RANDOM%.json"

REM Создание JSON payload
(
echo {
echo     "project": "%PROJECT_NAME%",
echo     "task": "%TASK_DESCRIPTION%",
echo     "task_id": "%TASK_ID%",
echo     "agent": "%AGENT_NAME%",
echo     "result": "%RESULT%",
) > "%JSON_FILE%"

REM Добавляем duration_seconds если указан
if defined DURATION_SECONDS (
    echo     "duration_seconds": %DURATION_SECONDS%, >> "%JSON_FILE%"
) else (
    echo     "metadata": { >> "%JSON_FILE%"
    goto :add_metadata
)

:add_metadata
echo         "script": "send_finish.bat", >> "%JSON_FILE%"
echo         "timestamp": "%date% %time%", >> "%JSON_FILE%"
echo         "hostname": "%COMPUTERNAME%", >> "%JSON_FILE%"
echo         "user": "%USERNAME%" >> "%JSON_FILE%"

if defined DURATION_SECONDS (
    echo     }, >> "%JSON_FILE%"
) else (
    echo     } >> "%JSON_FILE%"
)

echo } >> "%JSON_FILE%"

echo 🎉 Отправка вебхука о завершении задачи...
echo Проект: %PROJECT_NAME%
echo Задача: %TASK_DESCRIPTION%
echo Агент: %AGENT_NAME%
echo Task ID: %TASK_ID%
echo Результат: %RESULT%
if defined DURATION_SECONDS echo Длительность: %DURATION_SECONDS% секунд
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
echo 📋 Детали задачи:
echo Task ID: %TASK_ID%
echo Project: %PROJECT_NAME%
echo Agent: %AGENT_NAME%
echo Статус: ✅ Завершена

endlocal