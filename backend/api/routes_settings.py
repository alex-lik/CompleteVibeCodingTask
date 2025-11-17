"""
API роуты для работы с настройками пользователя
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from fastapi import Query
from pydantic import BaseModel

from core.database import get_db
from core.security import get_api_key
from models.models import UserSettings
from services.settings_service import SettingsService
from models.schemas import SettingsResponse, SettingsCreateResponse, SettingsUpdateRequest

settings_router = APIRouter()


@settings_router.get("/settings", response_model=List[SettingsResponse])
async def get_all_settings(
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Получить все настройки (глобальные + пользовательские)
    """
    service = SettingsService(db)

    # Получаем user_id из api_key или используем api_key как user_id
    user_id = api_key

    settings = service.get_all_settings(user_id=user_id)

    return [SettingsResponse(**setting) for setting in settings]


@settings_router.get("/settings/{setting_key}", response_model=SettingsResponse)
async def get_setting(
    setting_key: str,
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Получить конкретную настройку
    """
    service = SettingsService(db)

    # Получаем user_id из api_key или используем api_key как user_id
    user_id = api_key

    setting = service.get_setting(setting_key, user_id)

    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    return SettingsResponse(**setting)


@settings_router.get("/user/settings", response_model=List[SettingsResponse])
async def get_user_settings(
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Получить только пользовательские настройки
    """
    service = SettingsService(db)

    # Получаем user_id из api_key или используем api_key как user_id
    user_id = api_key

    settings = service.get_user_settings(user_id)

    return [SettingsResponse(**setting) for setting in settings]


class SettingsCreateRequest(BaseModel):
    setting_key: str
    value: Any
    description: Optional[str] = None
    is_global: bool = False

    class Config:
        schema_extra = {
            "example": {
                "setting_key": "theme",
                "value": "dark",
                "description": "Тема интерфейса",
                "is_global": False
            }
        }


@settings_router.post("/settings", response_model=SettingsCreateResponse)
async def create_setting(
    request: SettingsCreateRequest,
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Создать или обновить настройку
    """
    service = SettingsService(db)

    # Получаем user_id из api_key или используем api_key как user_id
    user_id = api_key if not request.is_global else None

    # Глобальные настройки могут создаваться только с особым разрешением
    if request.is_global:
        # В реальном приложении здесь должна быть проверка прав
        # Пока просто разрешаем создание глобальных настроек
        pass

    try:
        setting = service.set_setting(
            key=request.setting_key,
            value=request.value,
            user_id=user_id,
            description=request.description,
            is_global=request.is_global
        )

        return SettingsCreateResponse(**setting)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create setting: {str(e)}")


@settings_router.put("/settings/{setting_key}", response_model=SettingsResponse)
async def update_setting(
    setting_key: str,
    request: SettingsUpdateRequest,
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Обновить существующую настройку
    """
    service = SettingsService(db)

    # Получаем user_id из api_key или используем api_key как user_id
    user_id = api_key

    # Проверяем существование настройки
    existing_setting = service.get_setting(setting_key, user_id)

    if not existing_setting and not request.is_global:
        raise HTTPException(status_code=404, detail="Setting not found")

    try:
        setting = service.set_setting(
            key=setting_key,
            value=request.value,
            user_id=user_id if not request.is_global else None,
            description=request.description,
            is_global=request.is_global
        )

        return SettingsResponse(**setting)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update setting: {str(e)}")


@settings_router.delete("/settings/{setting_key}")
async def delete_setting(
    setting_key: str,
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Удалить настройку
    """
    service = SettingsService(db)

    # Получаем user_id из api_key или используем api_key как user_id
    user_id = api_key

    # Проверяем существование настройки перед удалением
    existing_setting = service.get_setting(setting_key, user_id)

    if not existing_setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    success = service.delete_setting(setting_key, user_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete setting")

    return {"message": "Setting deleted successfully"}


@settings_router.delete("/user/settings")
async def delete_all_user_settings(
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Удалить все пользовательские настройки
    """
    service = SettingsService(db)

    # Получаем user_id из api_key или используем api_key как user_id
    user_id = api_key

    success = service.delete_all_user_settings(user_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete user settings")

    return {"message": "All user settings deleted successfully"}


@settings_router.get("/settings/batch")
async def get_settings_batch(
    keys: str,  # comma-separated keys
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Получить несколько настроек по ключам
    """
    service = SettingsService(db)

    # Получаем user_id из api_key или используем api_key как user_id
    user_id = api_key

    key_list = [key.strip() for key in keys.split(",") if key.strip()]

    result = {}
    for key in key_list:
        setting = service.get_setting(key, user_id)
        if setting:
            result[key] = setting

    return {"settings": result}