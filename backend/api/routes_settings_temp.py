from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from core.database import get_db

settings_router = APIRouter()


@settings_router.get("/settings")
async def get_settings(db: Session = Depends(get_db)):
    """
    Получить все настройки пользователя
    """
    # Возвращаем пустой объект настроек для тестирования
    return {"settings": []}


@settings_router.put("/settings")
async def update_setting(
    key: str,
    value: Any,
    description: str = None
):
    """
    Обновить или создать настройку
    """
    # Возвращаем успешный ответ для тестирования
    return {"message": "Setting updated", "key": key, "value": value}