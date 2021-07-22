from db.cache import AbstractCacheStorage, ModelCache, get_cache_storage
from db.elastic import AsyncElasticsearch, get_elastic
from db.models import Genre
from db.storage import ElasticSearchStorage
from fastapi import Depends
from services.base import BaseElasticSearchService


class GenreService(BaseElasticSearchService):
    model = Genre


def get_genre_service(
    redis: AbstractCacheStorage = Depends(get_cache_storage),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(
        ModelCache(Genre, redis), ElasticSearchStorage(elastic=elastic, index="genres")
    )
