from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
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

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


# API Response Models
class ProjectResponse(ProjectBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def task_count(self) -> int:
        return len(getattr(self, 'tasks', []))

    @property
    def active_task_count(self) -> int:
        if not hasattr(self, 'tasks'):
            return 0
        return sum(1 for task in self.tasks if task.status == "running")

    model_config = {"from_attributes": True}


class TaskResponse(TaskBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    progress: Optional[float] = None
    task_metadata: Optional[Dict[str, Any]] = None
    agent_name: Optional[str] = None

    @property
    def title(self) -> str:
        return getattr(self, 'title', self.task)

    @property
    def description(self) -> Optional[str]:
        return getattr(self, 'description', None)

    model_config = {"from_attributes": True}


class PaginationParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=100, description="Количество элементов на странице")
    offset: int = Field(default=0, ge=0, description="Смещение для пагинации")


class PaginatedProjectResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


class PaginatedTaskResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


class StatsResponse(BaseModel):
    total_projects: int
    total_tasks: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_duration: Optional[float] = None