"""
Сервис для работы с пользовательскими настройками
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from models.models import UserSettings


class SettingsService:
    """
    Сервис для управления пользовательскими настройками
    Поддерживает глобальные и пользовательские настройки
    """

    def __init__(self, db: Session):
        self.db = db

    def get_setting(self, key: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Получить значение настройки

        Args:
            key: Ключ настройки
            user_id: ID пользователя (для пользовательских настроек)

        Returns:
            Словарь с настройкой или None
        """
        # Сначала ищем пользовательскую настройку
        if user_id:
            setting = self.db.query(UserSettings).filter(
                UserSettings.key == key,
                UserSettings.user_id == user_id
            ).first()
            if setting:
                return {
                    "id": setting.id,
                    "key": setting.key,
                    "value": setting.value,
                    "description": setting.description,
                    "is_global": setting.is_global,
                    "created_at": setting.created_at,
                    "updated_at": setting.updated_at
                }

        # Если пользовательская настройка не найдена, ищем глобальную
        setting = self.db.query(UserSettings).filter(
            UserSettings.key == key,
            UserSettings.is_global == "true"
        ).first()

        if setting:
            return {
                "id": setting.id,
                "key": setting.key,
                "value": setting.value,
                "description": setting.description,
                "is_global": setting.is_global,
                "created_at": setting.created_at,
                "updated_at": setting.updated_at
            }

        return None

    def get_user_settings(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Получить все настройки пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Список всех пользовательских настроек
        """
        settings = self.db.query(UserSettings).filter(
            UserSettings.user_id == user_id,
            UserSettings.is_global == "false"
        ).all()

        return [
            {
                "id": setting.id,
                "key": setting.key,
                "value": setting.value,
                "description": setting.description,
                "is_global": setting.is_global,
                "created_at": setting.created_at,
                "updated_at": setting.updated_at
            }
            for setting in settings
        ]

    def get_all_settings(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить все настройки (глобальные + пользовательские)

        Args:
            user_id: ID пользователя (для получения его пользовательских настроек)

        Returns:
            Список всех настроек
        """
        all_settings = []

        # Глобальные настройки
        global_settings = self.db.query(UserSettings).filter(
            UserSettings.is_global == "true"
        ).all()

        all_settings.extend([
            {
                "id": setting.id,
                "key": setting.key,
                "value": setting.value,
                "description": setting.description,
                "is_global": setting.is_global,
                "created_at": setting.created_at,
                "updated_at": setting.updated_at
            }
            for setting in global_settings
        ])

        # Пользовательские настройки
        if user_id:
            user_settings = self.db.query(UserSettings).filter(
                UserSettings.user_id == user_id,
                UserSettings.is_global == "false"
            ).all()

            all_settings.extend([
                {
                    "id": setting.id,
                    "key": setting.key,
                    "value": setting.value,
                    "description": setting.description,
                    "is_global": setting.is_global,
                    "created_at": setting.created_at,
                    "updated_at": setting.updated_at
                }
                for setting in user_settings
            ])

        return all_settings

    def set_setting(self, key: str, value: Any, user_id: Optional[str] = None,
                   description: Optional[str] = None, is_global: bool = False) -> Dict[str, Any]:
        """
        Установить значение настройки

        Args:
            key: Ключ настройки
            value: Значение (будет сериализовано в JSON)
            user_id: ID пользователя (для пользовательских настроек)
            description: Описание настройки
            is_global: Является ли настройка глобальной

        Returns:
            Созданная/обновленная настройка
        """
        existing_setting = None

        # Проверяем существование настройки
        if user_id:
            existing_setting = self.db.query(UserSettings).filter(
                UserSettings.key == key,
                UserSettings.user_id == user_id
            ).first()
        elif is_global:
            existing_setting = self.db.query(UserSettings).filter(
                UserSettings.key == key,
                UserSettings.is_global == "true"
            ).first()

        if existing_setting:
            # Обновляем существующую настройку
            existing_setting.value = value
            existing_setting.description = description
            existing_setting.updated_at = datetime.now(timezone.utc)

            if is_global:
                existing_setting.is_global = "true"
                existing_setting.user_id = None
            else:
                existing_setting.is_global = "false"
                existing_setting.user_id = user_id

            self.db.commit()
            self.db.refresh(existing_setting)

            return {
                "id": existing_setting.id,
                "key": existing_setting.key,
                "value": existing_setting.value,
                "description": existing_setting.description,
                "is_global": existing_setting.is_global,
                "created_at": existing_setting.created_at,
                "updated_at": existing_setting.updated_at
            }
        else:
            # Создаем новую настройку
            new_setting = UserSettings(
                key=key,
                value=value,
                description=description,
                is_global="true" if is_global else "false",
                user_id=None if is_global else user_id
            )

            self.db.add(new_setting)
            self.db.commit()
            self.db.refresh(new_setting)

            return {
                "id": new_setting.id,
                "key": new_setting.key,
                "value": new_setting.value,
                "description": new_setting.description,
                "is_global": new_setting.is_global,
                "created_at": new_setting.created_at,
                "updated_at": new_setting.updated_at
            }

    def delete_setting(self, key: str, user_id: Optional[str] = None) -> bool:
        """
        Удалить настройку

        Args:
            key: Ключ настройки
            user_id: ID пользователя (для пользовательских настроек)

        Returns:
            True если настройка удалена, False если не найдена
        """
        query = self.db.query(UserSettings)

        if user_id:
            query = query.filter(
                UserSettings.key == key,
                UserSettings.user_id == user_id
            )
        else:
            # Удаляем только глобальные настройки
            query = query.filter(
                UserSettings.key == key,
                UserSettings.is_global == "true"
            )

        setting = query.first()

        if setting:
            self.db.delete(setting)
            self.db.commit()
            return True

        return False

    def delete_all_user_settings(self, user_id: str) -> bool:
        """
        Удалить все пользовательские настройки

        Args:
            user_id: ID пользователя

        Returns:
            True если настройки удалены
        """
        settings = self.db.query(UserSettings).filter(
            UserSettings.user_id == user_id,
            UserSettings.is_global == "false"
        ).all()

        if settings:
            for setting in settings:
                self.db.delete(setting)
            self.db.commit()
            return True

        return False


# Глобальный экземпляр сервиса для использования в роутерах
settings_service = SettingsService