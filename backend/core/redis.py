import redis.asyncio as redis
from typing import Optional
import json
import pickle
from core.config import settings


class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Подключение к Redis"""
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False
        )
        # Проверяем подключение
        await self.redis.ping()
        print("Connected to Redis successfully!")

    async def disconnect(self):
        """Отключение от Redis"""
        if self.redis:
            await self.redis.close()
            print("Disconnected from Redis")

    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """Сохранение строки"""
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        """Получение строки"""
        result = await self.redis.get(key)
        return result.decode('utf-8') if result else None

    async def set_json(self, key: str, value: dict, expire: Optional[int] = None):
        """Сохранение JSON объекта"""
        json_str = json.dumps(value, ensure_ascii=False)
        await self.redis.set(key, json_str, ex=expire)

    async def get_json(self, key: str) -> Optional[dict]:
        """Получение JSON объекта"""
        result = await self.redis.get(key)
        if result:
            return json.loads(result.decode('utf-8'))
        return None

    async def set_object(self, key: str, value: any, expire: Optional[int] = None):
        """Сохранение объекта через pickle"""
        serialized = pickle.dumps(value)
        await self.redis.set(key, serialized, ex=expire)

    async def get_object(self, key: str) -> Optional[any]:
        """Получение объекта через pickle"""
        result = await self.redis.get(key)
        if result:
            return pickle.loads(result)
        return None

    async def delete(self, key: str):
        """Удаление ключа"""
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        return await self.redis.exists(key) > 0

    async def keys(self, pattern: str = "*") -> list:
        """Получение ключей по шаблону"""
        keys = await self.redis.keys(pattern)
        return [key.decode('utf-8') for key in keys]

    async def flushdb(self):
        """Очистка текущей базы данных"""
        await self.redis.flushdb()


# Глобальный экземпляр для использования в приложении
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency для FastAPI"""
    if not redis_client.redis:
        await redis_client.connect()
    return redis_client