from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from typing import Optional

from core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Общая функция проверки API ключа для всех эндпоинтов
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required"
        )

    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

    return api_key


async def get_api_key_optional(api_key: Optional[str] = Depends(api_key_header)) -> Optional[str]:
    """
    Опциональная проверка API ключа (для публичных эндпоинтов)
    """
    if api_key and api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key


async def verify_websocket_connection(api_key: Optional[str] = None) -> bool:
    """
    Проверка API ключа для WebSocket подключений
    """
    if api_key and api_key != settings.API_KEY:
        return False
    return True


def verify_api_key(api_key: str) -> bool:
    """
    Простая проверка API ключа
    """
    return api_key == settings.API_KEY