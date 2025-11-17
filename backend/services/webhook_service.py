from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from models.models import Project, Agent, Task
from models.schemas import WebhookStart, WebhookFinish, WebhookStatus, WebhookError


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
        return task

    def handle_status_webhook(self, data: WebhookStatus) -> Optional[Task]:
        """Обработать вебхук статуса задачи"""
        task = self.db.query(Task).filter(Task.task_id == data.task_id).first()

        if not task:
            return None

        task.status = data.status
        task.progress = data.progress
        task.task_metadata = data.metadata

        if data.message:
            task.description = data.message

        self.db.commit()
        self.db.refresh(task)
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
        return task