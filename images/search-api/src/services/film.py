import logging
from functools import cache
from typing import Optional

from db.cache import AbstractCacheStorage, ModelCache, get_cache_storage
from db.elastic import get_elastic
from db.models import Film
from db.storage import FilmSearchStorage
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Q, Search
from fastapi import Depends
from services.base import BaseElasticSearchService

logger = logging.getLogger(__name__)


class ElasticSearchFilmQueryBuilder:
    @staticmethod
    def prepare_query(
        s: Search,
        search_query: str = "",
        sort: Optional[str] = None,
        genre_filter: Optional[str] = None,
        filter_premium: bool = True,
    ) -> Search:
        if search_query:
            multi_match_fields = [
                "title^4",
                "description^3",
                "genres_names^2",
                "actors_names^4",
                "writers_names",
                "directors_names^3",
            ]
            s = s.query("multi_match", query=search_query, fields=multi_match_fields)
        if genre_filter:
            s = s.query(
                "nested",
                path="genres",
                query=Q("bool", filter=Q("term", genres__uuid=genre_filter)),
            )
        if filter_premium:
            s = s.filter("terms", premium=[False])
        if sort:
            s = s.sort(sort)
        return s


class FilmService(BaseElasticSearchService):
    model = Film


@cache
def get_film_service(
    redis: AbstractCacheStorage = Depends(get_cache_storage),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(
        ModelCache(Film, redis),
        FilmSearchStorage(
            elastic=elastic, index="movies", query_builder=ElasticSearchFilmQueryBuilder
        ),
    )
