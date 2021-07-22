import json
import logging
from typing import List, Optional, Protocol, Type

import aioredis
import registry
from aioredis import Redis
from config import config
from pydantic import BaseModel
from pydantic.tools import parse_raw_as
import backoff

logger = logging.getLogger(__name__)


class AbstractCacheStorage(Protocol):
    async def get(self, key: str) -> Optional[str]:
        ...

    async def set(self, key: str, value: str) -> None:
        ...

    async def close(self) -> None:
        ...


class RedisCacheStorage(AbstractCacheStorage):
    def __init__(self, redis: Redis, ttl: int = 60 * 5) -> None:
        self._redis = redis
        self._ttl = ttl

    async def close(self) -> None:
        await self._redis.close()

    async def get(self, key: str) -> Optional[str]:
        logger.debug(f"Trying to get from cache {key=}")
        data = await self._redis.get(key)
        return data

    async def set(self, key: str, value: str) -> None:
        logger.debug(f"Set cache with {key=}")
        await self._redis.set(key, value, expire=self._ttl)


class ModelCache:
    def __init__(self, model_class: Type[BaseModel], storage: AbstractCacheStorage):
        self.model_class = model_class
        self.storage = storage

    async def get_by_id(self, film_id: str) -> Optional[BaseModel]:
        key = f"{self.model_class.__name__}:id:{film_id}"
        if registry.filter_premium.get():
            key += ":safe"
        data = await self.storage.get(key)
        if not data:
            return None
        return self.model_class.parse_raw(data)

    async def set_by_id(self, film_id: str, value: BaseModel) -> None:
        key = f"{self.model_class.__name__}:id:{film_id}"
        if registry.filter_premium.get():
            key += ":safe"
        await self.storage.set(key=key, value=value.json())

    async def get_by_elastic_query(
        self, query_elastic: dict
    ) -> Optional[List[BaseModel]]:
        key = f"{self.model_class.__name__}:query:{str(query_elastic)}"
        if registry.filter_premium.get():
            key += ":safe"
        data = await self.storage.get(key)
        if not data:
            return None
        return parse_raw_as(List[self.model_class], data)

    async def set_by_elastic_query(
        self, query_elastic: dict, values: List[BaseModel]
    ) -> None:
        key = f"{self.model_class.__name__}:query:{str(query_elastic)}"
        if registry.filter_premium.get():
            key += ":safe"
        await self.storage.set(
            key=key, value=json.dumps([value.dict() for value in values])
        )


cache: Optional[AbstractCacheStorage] = None

@backoff.on_exception(backoff.expo, ConnectionError)
async def get_cache_storage() -> AbstractCacheStorage:
    global cache
    if not cache:
        redis = await aioredis.create_redis_pool(
            (config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20
        )
        cache = RedisCacheStorage(redis=redis, ttl=config.CACHE_TTL)
    return cache
