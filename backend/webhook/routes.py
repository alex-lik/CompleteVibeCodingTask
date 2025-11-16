from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from typing import Dict, Any

from models.schemas import WebhookStart, WebhookFinish, WebhookStatus, WebhookError
from core.config import settings

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
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Принимает вебхук о начале выполнения задачи
    """
    # TODO: Сохранить в базу данных
    # TODO: Отправить WebSocket уведомление

    return {
        "status": "accepted",
        "message": "Task started",
        "task_id": data.task_id,
        "project": data.project
    }


@webhook_router.post("/finish", status_code=status.HTTP_202_ACCEPTED)
async def webhook_finish(
    data: WebhookFinish,
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Принимает вебхук о завершении задачи
    """
    # TODO: Обновить в базе данных
    # TODO: Отправить WebSocket уведомление

    return {
        "status": "accepted",
        "message": "Task finished",
        "task_id": data.task_id,
        "project": data.project
    }


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