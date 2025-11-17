from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timezone

from core.database import get_db
from models.models import Project, Task
from models.schemas import ProjectResponse, TaskResponse, StatsResponse
from services.websocket_service import websocket_service

api_router = APIRouter()


@api_router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    """
    Получить список всех проектов
    """
    projects = db.query(Project).all()
    return projects


@api_router.get("/projects/{project_name}", response_model=ProjectResponse)
async def get_project(project_name: str, db: Session = Depends(get_db)):
    """
    Получить информацию о конкретном проекте
    """
    project = db.query(Project).filter(Project.name == project_name).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@api_router.get("/projects/{project_name}/tasks", response_model=List[TaskResponse])
async def get_project_tasks(
    project_name: str,
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получить список задач проекта с пагинацией и фильтрацией
    """
    project = db.query(Project).filter(Project.name == project_name).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    query = db.query(Task).filter(Task.project_id == project.id)

    if status:
        query = query.filter(Task.status == status)

    tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()
    return tasks


@api_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Получить детальную информацию о задаче
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@api_router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Получить общую статистику
    """
    # Общая статистика
    total_projects = db.query(Project).count()
    total_tasks = db.query(Task).count()

    # Статистика по статусам
    active_tasks = db.query(Task).filter(Task.status == "running").count()
    completed_tasks = db.query(Task).filter(Task.status == "completed").count()
    failed_tasks = db.query(Task).filter(Task.status == "failed").count()

    # Средняя длительность выполненных задач
    avg_duration_query = db.query(
        func.avg(func.extract('epoch', Task.finished_at) - func.extract('epoch', Task.started_at))
    ).filter(
        and_(
            Task.status == "completed",
            Task.finished_at.isnot(None),
            Task.started_at.isnot(None)
        )
    )

    avg_duration = avg_duration_query.scalar()
    average_duration = float(avg_duration) if avg_duration else None

    return StatsResponse(
        total_projects=total_projects,
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
        average_duration=average_duration
    )


@api_router.get("/websocket/stats")
async def get_websocket_stats():
    """
    Получить статистику WebSocket подключений
    """
    from fastapi.responses import JSONResponse
    return JSONResponse(content=websocket_service.get_connection_stats())