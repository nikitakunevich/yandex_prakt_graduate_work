import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from db.cache import ModelCache
from db.models import BaseESModel
from db.storage import AbstractStorage
from pydantic import parse_obj_as

logger = logging.getLogger(__name__)


class AbstractService(ABC):
    # TODO: replace ModelCache with AbstractCache
    def __init__(self, cache: ModelCache, storage: AbstractStorage):
        self.cache = cache
        self.storage = storage

    @abstractmethod
    async def get_model(self):
        pass

    @abstractmethod
    async def search(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_by_id(self, instance_id: str, **kwargs):
        pass

    @abstractmethod
    async def bulk_get_by_ids(self, ids: List[str], **kwargs):
        pass


class BaseElasticSearchService(AbstractService):
    model = None

    def __init__(self, cache: ModelCache, storage: AbstractStorage):
        super(BaseElasticSearchService, self).__init__(cache, storage)

    def get_model(self):
        if not self.model:
            raise Exception("Missing model")
        return self.model

    async def get_by_id(self, instance_id: str, **kwargs):
        instance = await self.cache.get_by_id(instance_id)
        if not instance:
            instance_data = await self.storage.get_by_id(instance_id, **kwargs)
            if not instance_data:
                return None
            model = self.get_model()
            instance = model(**instance_data)
            logger.debug(f"got {instance.__class__.__name__} from elastic: {instance}")
            await self.cache.set_by_id(instance_id, instance)
        return instance

    async def search(
        self,
        search_query: str,
        sort: Optional[str] = None,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        **kwargs,
    ):
        query = await self.storage.build_search_query(
            search_query=search_query,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            **kwargs,
        )
        items = await self.cache.get_by_elastic_query(query)
        if not items:
            items_data = await self.storage.search(query=query)
            model = self.get_model()
            items = parse_obj_as(List[model], items_data)
            await self.cache.set_by_elastic_query(query, items)
        return items

    async def bulk_get_by_ids(self, ids: List[str], **kwargs) -> List:
        if not ids:
            return []
        # noinspection PyTypeChecker
        instances = await asyncio.gather(
            *[self.cache.get_by_id(instance_id) for instance_id in ids]
        )
        instances: List[BaseESModel] = [
            instance for instance in instances if instance is not None
        ]
        instance_id_mapping = {instance.uuid: instance for instance in instances}
        not_cached_ids = [
            instance_id for instance_id in ids if instance_id not in instance_id_mapping
        ]

        res = await self.storage.bulk_get_by_ids(not_cached_ids)
        model = self.get_model()
        instances.extend(parse_obj_as(List[model], res))
        if instances:
            await asyncio.gather(
                *[
                    self.cache.set_by_id(instance.uuid, instance)
                    for instance in instances
                ]
            )
        if not instances:
            return []
        return instances
