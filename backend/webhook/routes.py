from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from typing import Dict, Any
from sqlalchemy.orm import Session

from models.schemas import WebhookStart, WebhookFinish, WebhookStatus, WebhookError
from core.config import settings
from core.database import get_db
from services.webhook_service import WebhookService
# from services.websocket_service import websocket_service  # Временно отключен

webhook_router = APIRouter()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key


@webhook_router.post("/start", status_code=status.HTTP_202_ACCEPTED)
async def webhook_start(
    data: WebhookStart,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Принимает вебхук о начале выполнения задачи
    """
    webhook_service = WebhookService(db)

    try:
        task = webhook_service.handle_start_webhook(data)

        # TODO: Отправить WebSocket уведомление (временно отключено)
        # await websocket_service.notify_task_started({
        #     "task_id": data.task_id,
        #     "project": data.project,
        #     "task": data.task,
        #     "agent": data.agent,
        #     "status": task.status,
        #     "database_id": task.id,
        #     "started_at": task.started_at.isoformat() if task.started_at else None,
        #     "metadata": data.metadata
        # })

        return {
            "status": "accepted",
            "message": "Task started successfully",
            "task_id": data.task_id,
            "project": data.project,
            "database_id": task.id,
            "status_in_db": task.status
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


@webhook_router.post("/finish", status_code=status.HTTP_202_ACCEPTED)
async def webhook_finish(
    data: WebhookFinish,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Принимает вебхук о завершении задачи
    """
    webhook_service = WebhookService(db)

    try:
        task = webhook_service.handle_finish_webhook(data)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {data.task_id} not found"
            )

        # TODO: Отправить WebSocket уведомление (временно отключено)
        # await websocket_service.notify_task_finished({
        #     "task_id": data.task_id,
        #     "project": data.project,
        #     "task": data.task,
        #     "agent": data.agent,
        #     "status": task.status,
        #     "database_id": task.id,
        #     "finished_at": task.finished_at.isoformat() if task.finished_at else None,
        #     "duration_seconds": task.duration_seconds,
        #     "result": data.result,
        #     "metadata": data.metadata
        # })

        return {
            "status": "accepted",
            "message": "Task finished successfully",
            "task_id": data.task_id,
            "project": data.project,
            "database_id": task.id,
            "status_in_db": task.status,
            "duration_seconds": task.duration_seconds
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


@webhook_router.post("/status", status_code=status.HTTP_202_ACCEPTED)
async def webhook_status(
    data: WebhookStatus,
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Принимает вебхук о статусе задачи
    """
    # TODO: Обновить в базе данных
    # TODO: Отправить WebSocket уведомление

    return {
        "status": "accepted",
        "message": "Status updated",
        "task_id": data.task_id,
        "project": data.project
    }


@webhook_router.post("/error", status_code=status.HTTP_202_ACCEPTED)
async def webhook_error(
    data: WebhookError,
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Принимает вебхук об ошибке
    """
    # TODO: Сохранить в базу данных
    # TODO: Отправить WebSocket уведомление

    return {
        "status": "accepted",
        "message": "Error logged",
        "task_id": data.task_id,
        "project": data.project
    }