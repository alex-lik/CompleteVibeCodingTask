from typing import Dict, List, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import asyncio


class WebSocketService:
    def __init__(self):
        # Хранилище активных подключений по проектам
        self.project_connections: Dict[str, Set[WebSocket]] = {}
        # Хранилище всех подключений
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, project: str = None):
        """Принять новое WebSocket подключение"""
        await websocket.accept()
        self.active_connections.add(websocket)

        if project:
            if project not in self.project_connections:
                self.project_connections[project] = set()
            self.project_connections[project].add(websocket)

        # Отправляем приветственное сообщение
        await self.send_personal_message({
            "type": "connection",
            "message": "Connected to Agent Task Tracker",
            "project": project,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

    def disconnect(self, websocket: WebSocket, project: str = None):
        """Отключить WebSocket"""
        self.active_connections.discard(websocket)

        if project and project in self.project_connections:
            self.project_connections[project].discard(websocket)
            # Удаляем пустые проекты
            if not self.project_connections[project]:
                del self.project_connections[project]

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Отправить сообщение конкретному клиенту"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            # Если соединение сломалось, удаляем его
            self.active_connections.discard(websocket)

    async def broadcast_to_project(self, message: Dict[str, Any], project: str):
        """Отправить сообщение всем клиентам конкретного проекта"""
        if project in self.project_connections:
            disconnected_clients = []
            for connection in self.project_connections[project]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    disconnected_clients.append(connection)

            # Удаляем отключенных клиентов
            for client in disconnected_clients:
                self.disconnect(client, project)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Отправить сообщение всем подключенным клиентам"""
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                disconnected_clients.append(connection)

        # Удаляем отключенных клиентов
        for client in disconnected_clients:
            self.disconnect(client)

    async def notify_task_started(self, task_data: Dict[str, Any]):
        """Отправить уведомление о начале задачи"""
        message = {
            "type": "task_started",
            "data": task_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Отправляем всем клиентам проекта
        await self.broadcast_to_project(message, task_data["project"])

        # Также отправляем всем (для глобального дашборда)
        await self.broadcast_to_all(message)

    async def notify_task_finished(self, task_data: Dict[str, Any]):
        """Отправить уведомление о завершении задачи"""
        message = {
            "type": "task_finished",
            "data": task_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast_to_project(message, task_data["project"])
        await self.broadcast_to_all(message)

    async def notify_task_status_updated(self, task_data: Dict[str, Any]):
        """Отправить уведомление об обновлении статуса задачи"""
        message = {
            "type": "task_status_updated",
            "data": task_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast_to_project(message, task_data["project"])
        await self.broadcast_to_all(message)

    async def notify_task_error(self, task_data: Dict[str, Any]):
        """Отправить уведомление об ошибке задачи"""
        message = {
            "type": "task_error",
            "data": task_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast_to_project(message, task_data["project"])
        await self.broadcast_to_all(message)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Получить статистику подключений"""
        return {
            "total_connections": len(self.active_connections),
            "project_connections": {
                project: len(connections)
                for project, connections in self.project_connections.items()
            }
        }


# Глобальный экземпляр сервиса
websocket_service = WebSocketService()