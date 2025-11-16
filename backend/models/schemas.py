from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class WebhookBase(BaseModel):
    project: str = Field(..., description="Название проекта")
    task: str = Field(..., description="Описание задачи")
    task_id: str = Field(..., description="Уникальный ID задачи")
    agent: str = Field(..., description="Имя агента")


class WebhookStart(WebhookBase):
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Дополнительные метаданные")


class WebhookFinish(WebhookBase):
    result: Optional[str] = Field(default=None, description="Результат выполнения")
    duration_seconds: Optional[float] = Field(default=None, description="Длительность в секундах")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Дополнительные метаданные")


class WebhookStatus(WebhookBase):
    status: str = Field(..., description="Текущий статус")
    progress: Optional[float] = Field(default=None, description="Прогресс в процентах")
    message: Optional[str] = Field(default=None, description="Сообщение о статусе")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Дополнительные метаданные")


class WebhookError(WebhookBase):
    error_type: str = Field(..., description="Тип ошибки")
    error_message: str = Field(..., description="Сообщение об ошибке")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Дополнительные метаданные")


# Database Models
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    task_count: int = 0
    active_task_count: int = 0

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    project_id: int
    task_id: str
    task: str
    agent: str
    status: str = "pending"


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True