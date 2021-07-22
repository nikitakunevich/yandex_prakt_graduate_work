import asyncio
from operator import attrgetter
from typing import List

import aiohttp
import aioredis
import pydantic
import pytest

from elasticsearch import AsyncElasticsearch
from starlette import status

import api_v1.models
import db.models


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def genres(es_client):
    action_films = [
        'a7334652-f73e-4f2b-88dd-f3ef08ee4cea',
        'c66258d4-9a34-47d0-85cc-5d4584090207',
    ]
    documentary_films = [
        '0c13e610-84f3-4573-9301-2df5235fe627',
        'a5a69721-a1ba-4d74-a1f9-905ddaac0eed',
    ]
    horror_films = [
        'a7334652-f73e-4f2b-88dd-f3ef08ee4cea',
    ]
    genres = [
        db.models.Genre(uuid='5017d3c9-3cb5-4cd1-a329-3c99a253bcf3', name='Action', film_ids=action_films),
        db.models.Genre(uuid='59e89fb7-639c-41fa-b829-a9261bad1114', name='Documentary', film_ids=documentary_films),
        db.models.Genre(uuid='9854793d-bb4f-45bf-8b2f-934bbf42adc9', name='Horror', film_ids=horror_films),
    ]
    create_genres_coros = [es_client.index('genres', id=genre.uuid, body=genre.dict(), refresh='wait_for')
                           for genre in genres]
    await asyncio.gather(*create_genres_coros)
    return genres


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_can_get_all_genres(session: aiohttp.ClientSession, es_client: AsyncElasticsearch, make_get_request,
                                  genres):
    # GIVEN multiple genres

    # WHEN query for all genres
    all_genres_response = await make_get_request('/genre/')
    received = pydantic.parse_obj_as(List[api_v1.models.Genre], all_genres_response.body)

    # THEN all genres are returned
    expected = [api_v1.models.Genre.from_db_model(genre) for genre in genres]
    assert sorted(expected, key=attrgetter('uuid')) == sorted(received, key=attrgetter('uuid'))


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_genres_sort_valid(session: aiohttp.ClientSession, es_client: AsyncElasticsearch, make_get_request,
                                 genres):
    # GIVEN some genres

    # WHEN sorted by name DESC
    all_genres_response = await make_get_request('/genre/', {"sort": "-name"})

    # THEN all genres are returned by name DESC
    received = pydantic.parse_obj_as(List[api_v1.models.Genre], all_genres_response.body)
    expected = [api_v1.models.Genre.from_db_model(genre) for genre in genres]
    expected = sorted(expected, key=attrgetter('name'), reverse=True)
    assert expected == received


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_genres_sort_unknown_name(session: aiohttp.ClientSession, es_client: AsyncElasticsearch, make_get_request,
                                        genres):
    # проверяем, что если нет такого имени сортировки, то ошибка
    r = await make_get_request('/genre/', {"sort": "-weird_name"})
    assert r.status == status.HTTP_400_BAD_REQUEST

# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_genres_sort_invalid_name(session: aiohttp.ClientSession, es_client: AsyncElasticsearch,
                                        make_get_request, genres):
    # проверяем, что если некорртектное имя параметра, то ошибка
    r = await make_get_request('/genre/', {"sort": "!@#$"})
    assert r.status == status.HTTP_422_UNPROCESSABLE_ENTITY


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_genres_query_in_cache(session: aiohttp.ClientSession, es_client: AsyncElasticsearch,
                                     redis: aioredis.Redis, make_get_request, genres):
    # GIVEN some genres
    page_number = 1
    page_size = 2
    first_two_genres_response = await make_get_request('/genre/',
                                                       {'page[size]': page_size, 'page[number]': page_number})
    received_api_models = pydantic.parse_obj_as(List[api_v1.models.Genre], first_two_genres_response.body)
    redis_key = "Genre:query:{'from': 0, 'size': 2}:safe"
    cached_value = await redis.get(redis_key)
    assert cached_value
    cached_models = pydantic.parse_raw_as(List[db.models.Genre], cached_value)
    assert received_api_models == [api_v1.models.Genre.from_db_model(genre) for genre in cached_models]


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_genres_id_in_cache(session: aiohttp.ClientSession, es_client: AsyncElasticsearch,
                                  redis: aioredis.Redis, make_get_request, genres):
    # GIVEN some genres
    genre_response = await make_get_request('/genre/5017d3c9-3cb5-4cd1-a329-3c99a253bcf3')
    received_api_model = pydantic.parse_obj_as(api_v1.models.GenreDetail, genre_response.body)
    redis_key = "Genre:id:5017d3c9-3cb5-4cd1-a329-3c99a253bcf3:safe"

    cached_value = await redis.get(redis_key)
    assert cached_value
    cached_model = pydantic.parse_raw_as(db.models.Genre, cached_value)
    assert received_api_model == api_v1.models.GenreDetail.from_db_model(cached_model)


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_genres_id(session: aiohttp.ClientSession, es_client: AsyncElasticsearch, make_get_request, genres):
    # WHEN queries for genre
    action_genre = await make_get_request('/genre/5017d3c9-3cb5-4cd1-a329-3c99a253bcf3')

    # THEN only that genre is returned
    received = pydantic.parse_obj_as(api_v1.models.GenreDetail, action_genre.body)
    expected = [api_v1.models.GenreDetail.from_db_model(genre) for genre in genres if genre.name == 'Action'][0]
    assert expected == received


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_genres_paging_last(session: aiohttp.ClientSession, es_client: AsyncElasticsearch, make_get_request,
                                  genres):
    # WHEN пробуем получить только последний элемент
    all_genres = await make_get_request('/genre/', {'page[size]': 1, 'page[number]': 3})

    # THEN только один желемент возвращаем
    received = pydantic.parse_obj_as(list[api_v1.models.Genre], all_genres.body)
    assert len(received) == 1


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_genres_paging_unavailable(session: aiohttp.ClientSession, es_client: AsyncElasticsearch,
                                         make_get_request,
                                         genres):
    # WHEN пробуем получить недоступную страницу
    r = await make_get_request('/genre/', {'page[size]': 10000, 'page[number]': 100})
    assert r.status == status.HTTP_400_BAD_REQUEST


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_id_invalid(session: aiohttp.ClientSession, es_client: AsyncElasticsearch, make_get_request, genres):
    # WHEN queries for genre
    r = await make_get_request('/genre/random_id')
    assert r.status == status.HTTP_404_NOT_FOUND

    r = await make_get_request('/genre/0000')
    assert r.status == status.HTTP_404_NOT_FOUND
