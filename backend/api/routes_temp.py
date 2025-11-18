from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timezone

from core.database import get_db
from models.models import Project, Task, Agent
from models.schemas import ProjectResponse, TaskResponse, StatsResponse, PaginationParams, PaginatedProjectResponse, PaginatedTaskResponse
from services.websocket_service import websocket_service

api_router = APIRouter()


@api_router.get("/projects", response_model=PaginatedProjectResponse)
async def get_projects(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Получить список всех проектов с пагинацией
    """
    query = db.query(Project)
    total = query.count()
    projects = query.order_by(Project.created_at.desc()).offset(offset).limit(limit).all()

    return PaginatedProjectResponse(
        items=projects,
        total=total,
        limit=limit,
        offset=offset,
        has_next=offset + limit < total,
        has_prev=offset > 0
    )


@api_router.get("/projects/{project_name}", response_model=ProjectResponse)
async def get_project(
    project_name: str,
    db: Session = Depends(get_db)
):
    """
    Получить информацию о конкретном проекте
    """
    project = db.query(Project).filter(Project.name == project_name).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@api_router.get("/projects/{project_name}/tasks", response_model=PaginatedTaskResponse)
async def get_project_tasks(
    project_name: str,
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    task_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получить список задач проекта с пагинацией и расширенной фильтрацией
    """
    project = db.query(Project).filter(Project.name == project_name).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    query = db.query(Task).filter(Task.project_id == project.id)

    # Фильтры
    if status:
        query = query.filter(Task.status == status)


    if task_name:
        query = query.filter(Task.title.ilike(f"%{task_name}%"))

    if from_date:
        query = query.filter(Task.created_at >= from_date)

    if to_date:
        query = query.filter(Task.created_at <= to_date)

    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    # Create TaskResponse objects directly from models
    task_responses = []
    for task in tasks:
        task_response = TaskResponse(
            id=task.id,
            project_id=task.project_id,
            task_id=task.task_id,
            task=task.title,
            agent=task.agent.name if task.agent else "",
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
            started_at=task.started_at,
            finished_at=task.finished_at,
            result=task.result,
            error_message=task.error_message,
            duration_seconds=task.duration_seconds,
            progress=task.progress,
            task_metadata=task.task_metadata,
            agent_name=task.agent.name if task.agent else None
        )
        task_responses.append(task_response)

    return PaginatedTaskResponse(
        items=task_responses,
        total=total,
        limit=limit,
        offset=offset,
        has_next=offset + limit < total,
        has_prev=offset > 0
    )


@api_router.get("/tasks/search", response_model=PaginatedTaskResponse)
async def search_tasks(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    project_name: Optional[str] = None,
    task_name: Optional[str] = None,
    agent: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Поиск задач по всем проектам с расширенной фильтрацией
    """
    query = db.query(Task)

    # Фильтры
    if status:
        query = query.filter(Task.status == status)


    if project_name:
        query = query.join(Task.project).filter(Project.name == project_name)

    if task_name:
        query = query.filter(Task.title.ilike(f"%{task_name}%"))

    if agent:
        query = query.join(Task.agent).filter(Agent.name == agent)

    if from_date:
        query = query.filter(Task.created_at >= from_date)

    if to_date:
        query = query.filter(Task.created_at <= to_date)

    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    # Create TaskResponse objects directly from models
    task_responses = []
    for task in tasks:
        task_response = TaskResponse(
            id=task.id,
            project_id=task.project_id,
            task_id=task.task_id,
            task=task.title,
            agent=task.agent.name if task.agent else "",
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
            started_at=task.started_at,
            finished_at=task.finished_at,
            result=task.result,
            error_message=task.error_message,
            duration_seconds=task.duration_seconds,
            progress=task.progress,
            task_metadata=task.task_metadata,
            agent_name=task.agent.name if task.agent else None
        )
        task_responses.append(task_response)

    return PaginatedTaskResponse(
        items=task_responses,
        total=total,
        limit=limit,
        offset=offset,
        has_next=offset + limit < total,
        has_prev=offset > 0
    )


@api_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Получить детальную информацию о задаче
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        task_id=task.task_id,
        task=task.title,
        agent=task.agent.name if task.agent else "",
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
        started_at=task.started_at,
        finished_at=task.finished_at,
        result=task.result,
        error_message=task.error_message,
        duration_seconds=task.duration_seconds,
        progress=task.progress,
        task_metadata=task.task_metadata,
        agent_name=task.agent.name if task.agent else None
    )


@api_router.get("/stats/projects")
async def get_projects_stats(db: Session = Depends(get_db)):
    """
    Получить статистику по проектам
    """
    total_projects = db.query(Project).count()
    return {"total_projects": total_projects}


@api_router.get("/stats/tasks")
async def get_tasks_stats(db: Session = Depends(get_db)):
    """
    Получить статистику по задачам
    """
    total_tasks = db.query(Task).count()
    active_tasks = db.query(Task).filter(Task.status == "running").count()
    completed_tasks = db.query(Task).filter(Task.status == "completed").count()
    failed_tasks = db.query(Task).filter(Task.status == "failed").count()

    return {
        "total_tasks": total_tasks,
        "active_tasks": active_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks
    }


@api_router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: Session = Depends(get_db)
):
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