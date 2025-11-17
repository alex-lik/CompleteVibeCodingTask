"""
MCP Adapter for Agent Task Tracker

Этот модуль предоставляет MCP (Model Context Protocol) адаптер для интеграции
с AI-агентами, позволяя им отправлять вебхуки и получать статус задач.
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
from dataclasses import dataclass

from core.config import settings
from core.security import verify_api_key

logger = logging.getLogger(__name__)


@dataclass
class MCPConfig:
    """Конфигурация MCP адаптера"""
    base_url: str
    api_key: str
    timeout: int = 30
    retry_attempts: int = 3


class MCPAdapter:
    """
    MCP Adapter - предоставляет интерфейс для AI-агентов взаимодействия с системой
    """

    def __init__(self, config: Optional[MCPConfig] = None):
        self.config = config or MCPConfig(
            base_url=settings.BASE_URL,
            api_key=settings.API_KEY
        )
        self.session: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        self.session = httpx.AsyncClient(
            timeout=self.config.timeout,
            headers={"X-API-Key": self.config.api_key}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        if self.session:
            await self.session.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Выполнить HTTP-запрос к API"""
        if not self.session:
            raise RuntimeError("MCPAdapter must be used as async context manager")

        url = f"{self.config.base_url}{endpoint}"

        for attempt in range(self.config.retry_attempts):
            try:
                logger.info(f"MCP Request: {method} {url} (attempt {attempt + 1})")

                response = await self.session.request(method, url, json=data)

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"MCP Response: {result}")
                    return result
                else:
                    error_text = response.text
                    logger.error(f"MCP Error: {response.status_code} - {error_text}")

                    if response.status_code == 401:
                        raise ValueError("Invalid API key")
                    elif response.status_code == 404:
                        raise ValueError(f"Endpoint not found: {endpoint}")
                    else:
                        raise ValueError(f"API error: {response.status_code} - {error_text}")

            except httpx.RequestError as e:
                logger.warning(f"MCP Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.config.retry_attempts - 1:
                    raise
                await asyncio.sleep(1 * (attempt + 1))  # Экспоненциальная задержка

    async def start_task(
        self,
        project: str,
        task: str,
        task_id: str,
        agent: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Начать новую задачу

        Args:
            project: Название проекта
            task: Описание задачи
            task_id: Уникальный ID задачи
            agent: Имя агента
            metadata: Дополнительные метаданные

        Returns:
            Dict[str, Any]: Ответ от API
        """
        payload = {
            "project": project,
            "task": task,
            "task_id": task_id,
            "agent": agent,
            "metadata": metadata or {}
        }

        return await self._make_request("POST", "/webhook/start", payload)

    async def finish_task(
        self,
        project: str,
        task: str,
        task_id: str,
        agent: str,
        result: str,
        duration_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Завершить задачу

        Args:
            project: Название проекта
            task: Описание задачи
            task_id: Уникальный ID задачи
            agent: Имя агента
            result: Результат выполнения задачи
            duration_seconds: Длительность выполнения в секундах
            metadata: Дополнительные метаданные

        Returns:
            Dict[str, Any]: Ответ от API
        """
        payload = {
            "project": project,
            "task": task,
            "task_id": task_id,
            "agent": agent,
            "result": result,
            "metadata": metadata or {}
        }

        if duration_seconds:
            payload["duration_seconds"] = duration_seconds

        return await self._make_request("POST", "/webhook/finish", payload)

    async def update_status(
        self,
        project: str,
        task: str,
        task_id: str,
        agent: str,
        status: str,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Обновить статус задачи

        Args:
            project: Название проекта
            task: Описание задачи
            task_id: Уникальный ID задачи
            agent: Имя агента
            status: Новый статус
            progress: Прогресс в процентах (0-100)
            message: Сообщение о статусе
            metadata: Дополнительные метаданные

        Returns:
            Dict[str, Any]: Ответ от API
        """
        payload = {
            "project": project,
            "task": task,
            "task_id": task_id,
            "agent": agent,
            "status": status,
            "metadata": metadata or {}
        }

        if progress is not None:
            payload["progress"] = progress
        if message:
            payload["message"] = message

        return await self._make_request("POST", "/webhook/status", payload)

    async def report_error(
        self,
        project: str,
        task: str,
        task_id: str,
        agent: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Сообщить об ошибке

        Args:
            project: Название проекта
            task: Описание задачи
            task_id: Уникальный ID задачи
            agent: Имя агента
            error_type: Тип ошибки
            error_message: Сообщение об ошибке
            stack_trace: Stack trace ошибки
            metadata: Дополнительные метаданные

        Returns:
            Dict[str, Any]: Ответ от API
        """
        payload = {
            "project": project,
            "task": task,
            "task_id": task_id,
            "agent": agent,
            "error_type": error_type,
            "error_message": error_message,
            "metadata": metadata or {}
        }

        if stack_trace:
            payload["stack_trace"] = stack_trace

        return await self._make_request("POST", "/webhook/error", payload)

    async def get_projects(self) -> List[Dict[str, Any]]:
        """
        Получить список проектов

        Returns:
            List[Dict[str, Any]]: Список проектов
        """
        result = await self._make_request("GET", "/api/projects")
        return result.get("projects", [])

    async def get_project_tasks(
        self,
        project_name: str,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Получить задачи проекта

        Args:
            project_name: Название проекта
            limit: Лимит задач
            offset: Смещение
            status: Фильтр по статусу

        Returns:
            Dict[str, Any]: Задачи проекта с метаданными пагинации
        """
        params = f"?limit={limit}&offset={offset}"
        if status:
            params += f"&status={status}"

        result = await self._make_request("GET", f"/api/projects/{project_name}/tasks{params}")
        return result

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику системы

        Returns:
            Dict[str, Any]: Статистика
        """
        return await self._make_request("GET", "/api/stats")


class MCPContextManager:
    """
    Контекстный менеджер для упрощенной работы с MCP в AI-агентах
    """

    def __init__(self, agent_name: str, project_name: str):
        self.agent_name = agent_name
        self.project_name = project_name
        self.adapter: Optional[MCPAdapter] = None
        self.current_task_id: Optional[str] = None
        self.start_time: Optional[datetime] = None

    async def __aenter__(self):
        self.adapter = MCPAdapter()
        await self.adapter.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.adapter:
            await self.adapter.__aexit__(exc_type, exc_val, exc_tb)

    async def start_task(
        self,
        task_description: str,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Начать задачу и вернуть её ID"""
        if not task_id:
            task_id = f"{self.agent_name}-{int(datetime.now().timestamp())}"

        self.current_task_id = task_id
        self.start_time = datetime.now()

        await self.adapter.start_task(
            project=self.project_name,
            task=task_description,
            task_id=task_id,
            agent=self.agent_name,
            metadata=metadata
        )

        return task_id

    async def update_progress(
        self,
        progress: int,
        message: Optional[str] = None
    ) -> None:
        """Обновить прогресс текущей задачи"""
        if not self.current_task_id or not self.adapter:
            return

        await self.adapter.update_status(
            project=self.project_name,
            task="",  # Будет заполнено на сервере
            task_id=self.current_task_id,
            agent=self.agent_name,
            status="running",
            progress=progress,
            message=message
        )

    async def complete_task(
        self,
        result: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Завершить текущую задачу"""
        if not self.current_task_id or not self.adapter:
            return

        duration = None
        if self.start_time:
            duration = int((datetime.now() - self.start_time).total_seconds())

        await self.adapter.finish_task(
            project=self.project_name,
            task="",  # Будет заполнено на сервере
            task_id=self.current_task_id,
            agent=self.agent_name,
            result=result,
            duration_seconds=duration,
            metadata=metadata
        )

    async def fail_task(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None
    ) -> None:
        """Сообщить об ошибке в текущей задаче"""
        if not self.current_task_id or not self.adapter:
            return

        await self.adapter.report_error(
            project=self.project_name,
            task="",  # Будет заполнено на сервере
            task_id=self.current_task_id,
            agent=self.agent_name,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace
        )


# Удобная функция для создания MCP контекста
def create_mcp_context(agent_name: str, project_name: str) -> MCPContextManager:
    """
    Создать MCP контекст для агента

    Args:
        agent_name: Имя агента
        project_name: Имя проекта

    Returns:
        MCPContextManager: Контекст менеджер для работы с задачами
    """
    return MCPContextManager(agent_name, project_name)