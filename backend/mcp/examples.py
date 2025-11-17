"""
Примеры использования MCP адаптера для AI-агентов
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import create_mcp_context, MCPAdapter

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_simple_mcp_usage():
    """
    Простой пример использования MCP адаптера
    """
    print("=== Простой пример использования MCP ===")

    async with MCPAdapter() as mcp:
        # Начинаем задачу
        result = await mcp.start_task(
            project="example-project",
            task="Пример задачи с MCP адаптером",
            task_id="example-task-1",
            agent="example-agent",
            metadata={"version": "1.0", "environment": "test"}
        )
        print(f"Задача начата: {result}")

        # Обновляем статус
        await asyncio.sleep(1)
        result = await mcp.update_status(
            project="example-project",
            task="",
            task_id="example-task-1",
            agent="example-agent",
            status="running",
            progress=50,
            message="Выполнено половину работы"
        )
        print(f"Статус обновлен: {result}")

        # Завершаем задачу
        await asyncio.sleep(1)
        result = await mcp.finish_task(
            project="example-project",
            task="",
            task_id="example-task-1",
            agent="example-agent",
            result="Задача успешно выполнена через MCP адаптер",
            duration_seconds=2,
            metadata={"files_created": 1}
        )
        print(f"Задача завершена: {result}")


async def example_context_manager():
    """
    Пример использования MCP Context Manager для агента
    """
    print("\n=== Пример использования MCP Context Manager ===")

    async with create_mcp_context(
        agent_name="data-processor",
        project_name="data-analysis"
    ) as mcp_ctx:

        # Начинаем задачу
        task_id = await mcp_ctx.start_task(
            task_description="Анализ данных клиента",
            metadata={"dataset": "customers.csv", "records": 1000}
        )
        print(f"Начата задача: {task_id}")

        # Имитация работы с обновлением прогресса
        steps = [
            (25, "Загрузка данных"),
            (50, "Очистка данных"),
            (75, "Анализ статистики"),
            (90, "Генерация отчета"),
            (100, "Финализация")
        ]

        for progress, message in steps:
            await asyncio.sleep(0.5)
            await mcp_ctx.update_progress(progress, message)
            print(f"Прогресс: {progress}% - {message}")

        # Завершаем задачу
        await mcp_ctx.complete_task(
            result="Анализ данных завершен успешно. Найдено 3 аномалии.",
            metadata={
                "anomalies_found": 3,
                "processing_time": "2.5s",
                "report_generated": True
            }
        )
        print("Задача завершена успешно!")


async def example_error_handling():
    """
    Пример обработки ошибок через MCP
    """
    print("\n=== Пример обработки ошибок ===")

    async with MCPAdapter() as mcp:
        try:
            # Начинаем задачу, которая может завершиться ошибкой
            result = await mcp.start_task(
                project="error-example",
                task="Задача с возможной ошибкой",
                task_id="error-task-1",
                agent="error-prone-agent"
            )
            print(f"Задача начата: {result}")

            # Имитация ошибки
            await asyncio.sleep(0.5)

            # Сообщаем об ошибке
            result = await mcp.report_error(
                project="error-example",
                task="",
                task_id="error-task-1",
                agent="error-prone-agent",
                error_type="ValueError",
                error_message="Некорректные входные данные",
                stack_trace="Traceback (most recent call last):\n  File example.py, line 42\nValueError: Invalid input",
                metadata={"input_data": "corrupted_data.json"}
            )
            print(f"Ошибка зарегистрирована: {result}")

        except Exception as e:
            logger.error(f"Ошибка в MCP клиенте: {e}")


async def example_get_data():
    """
    Пример получения данных через MCP API
    """
    print("\n=== Пример получения данных ===")

    async with MCPAdapter() as mcp:
        try:
            # Получаем список проектов
            projects = await mcp.get_projects()
            print(f"Проекты: {projects}")

            # Получаем статистику
            stats = await mcp.get_stats()
            print(f"Статистика: {stats}")

            # Получаем задачи конкретного проекта (если проекты есть)
            if projects:
                first_project = projects[0]["name"]
                tasks = await mcp.get_project_tasks(
                    project_name=first_project,
                    limit=5,
                    status=None
                )
                print(f"Задачи проекта '{first_project}': {tasks}")

        except Exception as e:
            logger.error(f"Ошибка при получении данных: {e}")


async def example_agent_workflow():
    """
    Полный пример рабочего процесса AI-агента
    """
    print("\n=== Пример рабочего процесса AI-агента ===")

    async with create_mcp_context(
        agent_name="claude-3-5-sonnet",
        project_name="content-generation"
    ) as agent:

        try:
            # Шаг 1: Начинаем основную задачу
            main_task = await agent.start_task(
                task_description="Генерация технической документации",
                metadata={"doc_type": "api", "format": "markdown"}
            )
            print(f"Начата основная задача: {main_task}")

            # Шаг 2: Анализ требований
            await agent.update_progress(20, "Анализ требований к документации")
            await asyncio.sleep(0.3)

            # Шаг 3: Создание структуры
            await agent.update_progress(40, "Создание структуры документа")
            await asyncio.sleep(0.3)

            # Шаг 4: Написание контента
            await agent.update_progress(70, "Написание основного контента")
            await asyncio.sleep(0.3)

            # Шаг 5: Ревью и исправления
            await agent.update_progress(90, "Проверка и исправления")
            await asyncio.sleep(0.3)

            # Шаг 6: Завершение
            await agent.complete_task(
                result="Документация успешно сгенерирована. Создано 15 разделов, 50+ примеров кода.",
                metadata={
                    "sections_created": 15,
                    "code_examples": 52,
                    "word_count": 3500,
                    "format": "markdown",
                    "quality_score": 9.2
                }
            )
            print("Документация успешно сгенерирована!")

        except Exception as e:
            # Если произошла ошибка, сообщаем о ней
            await agent.fail_task(
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=None  # В реальном сценарии можно добавить stack trace
            )
            logger.error(f"Задача завершилась ошибкой: {e}")
            raise


async def main():
    """
    Основная функция для запуска всех примеров
    """
    print("🚀 Запуск примеров MCP адаптера\n")

    examples = [
        example_simple_mcp_usage,
        example_context_manager,
        example_error_handling,
        example_get_data,
        example_agent_workflow
    ]

    for example_func in examples:
        try:
            await example_func()
        except Exception as e:
            logger.error(f"Ошибка в примере {example_func.__name__}: {e}")

        print("\n" + "="*50 + "\n")

    print("✅ Все примеры выполнены!")


if __name__ == "__main__":
    # Запуск примеров
    asyncio.run(main())