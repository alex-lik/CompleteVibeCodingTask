from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from models.models import Project, Agent, Task
from models.schemas import WebhookStart, WebhookFinish, WebhookStatus, WebhookError
from services.websocket_service import websocket_service


class WebhookService:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_project(self, project_name: str) -> Project:
        """Получить или создать проект"""
        project = self.db.query(Project).filter(Project.name == project_name).first()
        if not project:
            project = Project(name=project_name)
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
        return project

    def _get_or_create_agent(self, agent_name: str) -> Agent:
        """Получить или создать агента"""
        agent = self.db.query(Agent).filter(Agent.name == agent_name).first()
        if not agent:
            agent = Agent(name=agent_name)
            self.db.add(agent)
            self.db.commit()
            self.db.refresh(agent)
        return agent

    def handle_start_webhook(self, data: WebhookStart) -> Task:
        """Обработать вебхук начала задачи"""
        # Получаем или создаем проект и агента
        project = self._get_or_create_project(data.project)
        agent = self._get_or_create_agent(data.agent)

        # Проверяем, существует ли задача
        task = self.db.query(Task).filter(Task.task_id == data.task_id).first()

        if task:
            # Обновляем существующую задачу
            task.title = data.task
            task.description = data.task  # Используем то же поле для описания
            task.status = "running"
            task.started_at = datetime.now(timezone.utc)
            task.task_metadata = data.metadata
            task.project_id = project.id
            task.agent_id = agent.id
        else:
            # Создаем новую задачу
            task = Task(
                task_id=data.task_id,
                title=data.task,
                description=data.task,
                status="running",
                started_at=datetime.now(timezone.utc),
                task_metadata=data.metadata,
                project_id=project.id,
                agent_id=agent.id
            )
            self.db.add(task)

        self.db.commit()
        self.db.refresh(task)

        # Отправляем WebSocket уведомление
        task_data = {
            "task_id": task.task_id,
            "title": task.title,
            "project": project.name,
            "agent": agent.name,
            "status": task.status,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "project_id": project.id
        }
        import asyncio
        asyncio.create_task(websocket_service.notify_task_started(task_data))

        return task

    def handle_finish_webhook(self, data: WebhookFinish) -> Optional[Task]:
        """Обработать вебхук завершения задачи"""
        task = self.db.query(Task).filter(Task.task_id == data.task_id).first()

        if not task:
            return None

        task.status = "completed"
        task.finished_at = datetime.utcnow()
        task.result = data.result
        task.duration_seconds = data.duration_seconds
        task.task_metadata = data.metadata

        self.db.commit()
        self.db.refresh(task)

        # Отправляем WebSocket уведомление
        project = self.db.query(Project).filter(Project.id == task.project_id).first()
        agent = self.db.query(Agent).filter(Agent.id == task.agent_id).first()

        if project:
            task_data = {
                "task_id": task.task_id,
                "title": task.title,
                "project": project.name,
                "agent": agent.name if agent else "Unknown",
                "status": task.status,
                "duration_seconds": task.duration_seconds,
                "finished_at": task.finished_at.isoformat() if task.finished_at else None,
                "result": task.result,
                "project_id": project.id
            }
            import asyncio
            asyncio.create_task(websocket_service.notify_task_finished(task_data))

        return task

    def handle_status_webhook(self, data: WebhookStatus) -> Optional[Task]:
        """Обработать вебхук статуса задачи"""
        task = self.db.query(Task).filter(Task.task_id == data.task_id).first()

        if not task:
            return None

        old_status = task.status
        task.status = data.status
        task.progress = data.progress
        task.task_metadata = data.metadata

        if data.message:
            task.description = data.message

        self.db.commit()
        self.db.refresh(task)

        # Отправляем WebSocket уведомление только если статус изменился
        if old_status != data.status:
            project = self.db.query(Project).filter(Project.id == task.project_id).first()
            agent = self.db.query(Agent).filter(Agent.id == task.agent_id).first()

            if project:
                task_data = {
                    "task_id": task.task_id,
                    "title": task.title,
                    "project": project.name,
                    "agent": agent.name if agent else "Unknown",
                    "status": task.status,
                    "progress": task.progress,
                    "message": data.message,
                    "project_id": project.id
                }
                import asyncio
                asyncio.create_task(websocket_service.notify_task_status_updated(task_data))

        return task

    def handle_error_webhook(self, data: WebhookError) -> Optional[Task]:
        """Обработать вебхук ошибки задачи"""
        task = self.db.query(Task).filter(Task.task_id == data.task_id).first()

        if not task:
            return None

        task.status = "failed"
        task.finished_at = datetime.utcnow()
        task.error_message = f"{data.error_type}: {data.error_message}"
        task.task_metadata = data.metadata

        if data.stack_trace:
            task.description = data.stack_trace

        self.db.commit()
        self.db.refresh(task)

        # Отправляем WebSocket уведомление
        project = self.db.query(Project).filter(Project.id == task.project_id).first()
        agent = self.db.query(Agent).filter(Agent.id == task.agent_id).first()

        if project:
            task_data = {
                "task_id": task.task_id,
                "title": task.title,
                "project": project.name,
                "agent": agent.name if agent else "Unknown",
                "status": task.status,
                "error_type": data.error_type,
                "error_message": data.error_message,
                "finished_at": task.finished_at.isoformat() if task.finished_at else None,
                "project_id": project.id
            }
            import asyncio
            asyncio.create_task(websocket_service.notify_task_error(task_data))

        return task