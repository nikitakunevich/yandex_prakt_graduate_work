import logging
from abc import ABC, abstractmethod
from typing import List, Optional

import elasticsearch
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search
from fastapi import HTTPException
from starlette import status

logger = logging.getLogger(__name__)


class AbstractStorage(ABC):
    @abstractmethod
    async def get_by_id(self, instance_id: str, **kwargs):
        pass

    @abstractmethod
    async def bulk_get_by_ids(self, ids: List[str]):
        pass

    @abstractmethod
    async def search(self, query: Search):
        pass

    @abstractmethod
    async def build_search_query(self, *args, **kwargs) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def prepare_query(s: Search, search_query, sort):
        pass

    @staticmethod
    @abstractmethod
    def get_paginated_query(*args, **kwargs):
        pass


class ElasticSearchStorage(AbstractStorage):
    def __init__(self, elastic: AsyncElasticsearch, index: str, query_builder=None):
        self._query_builder = query_builder
        self.elastic = elastic
        self.index = index

    async def get_by_id(self, instance_id: str, **kwargs) -> Optional[dict]:
        try:
            doc = await self.elastic.get(self.index, instance_id)
            return doc["_source"]
        except elasticsearch.exceptions.NotFoundError:
            return None

    async def bulk_get_by_ids(self, ids: List[str]) -> List[dict]:
        try:
            res = await self.elastic.mget(body={"ids": ids}, index=self.index)
            return [doc["_source"] for doc in res["docs"]]
        except elasticsearch.exceptions.NotFoundError:
            return []

    @staticmethod
    def prepare_query(s, search_query, sort):
        if search_query:
            s = s.query("match", full_name=search_query)
        if sort:
            s = s.sort(sort)
        return s

    async def build_search_query(
        self,
        search_query: str = "",
        sort: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 50,
        **kwargs,
    ) -> dict:
        s = Search(using=self.elastic, index=self.index)
        if not self._query_builder:
            s = self.prepare_query(s, search_query, sort)
        else:
            s = self._query_builder.prepare_query(s, search_query, sort, **kwargs)
        s = self.get_paginated_query(s, page_number, page_size)
        return s

    async def search(self, query: Search) -> List[dict]:
        try:
            search_result = await self.elastic.search(index=self.index, body=query)
        except elasticsearch.exceptions.RequestError as re:
            if re.error == "search_phase_execution_exception":
                # Если используется sort которого нет в elastic
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Malformed request")
            raise
        items = [hit["_source"] for hit in search_result["hits"]["hits"]]
        return items

    @staticmethod
    def get_paginated_query(search: Search, page_number: int, page_size: int) -> dict:
        start = (page_number - 1) * page_size
        return search[start : start + page_size].to_dict()


class FilmSearchStorage(ElasticSearchStorage):
    async def get_by_id(
        self, instance_id: str, filter_premium: bool = True, **kwargs
    ) -> Optional[dict]:
        film = await super().get_by_id(instance_id)
        if filter_premium and film and film["premium"]:
            return None
        return film

    async def bulk_get_by_ids(
        self, ids: List[str], filter_premium: bool = True, **kwargs
    ) -> List[dict]:
        films = await super().bulk_get_by_ids(ids)
        if filter_premium:
            for film in films:
                if not hasattr(film, "premium"):
                    logger.debug(f"film with no susp: {film}")
            return [film for film in films if not film["premium"]]
        else:
            return films
