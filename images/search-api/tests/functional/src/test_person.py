import asyncio
from typing import List

import pytest
from aioredis import Redis

from elasticsearch import AsyncElasticsearch

from db.models import Film, Person


@pytest.fixture
async def persons(es_client: AsyncElasticsearch):
    persons = [
        {
            "uuid": "0040371d-f875-4d42-ab17-ffaf3cacfb91",
            "full_name": "Chris Cooper",
            "roles": [
                "actor"
            ],
            "film_ids": [
                "93d538fe-1328-4b4c-a327-f61a80f25a3c"
            ]
        },
        {
            "uuid": "0040371d-f875-4d42-ab17-ffaf3cacfb92",
            "full_name": "June Laverick2",
            "roles": [
                "actor"
            ],
            "film_ids": [
                "93d538fe-1328-4b4c-a327-f61a80f25a3c",
                "93d538fe-1328-4b4c-a327-f61a80f20000"
            ]
        },
        {
            "uuid": "00573d04-34ba-4b52-808c-49c428af704d",
            "full_name": "June Laverick",
            "roles": [
                "actor"
            ],
            "film_ids": []
        }
    ]

    await asyncio.gather(
        *[es_client.index('persons', body=Person.parse_obj(person).dict(), id=person['uuid'], refresh='wait_for') for
          person in persons])
    return persons


@pytest.fixture
async def person_movies(es_client: AsyncElasticsearch):
    films = [
        {
            'uuid': '93d538fe-1328-4b4c-a327-f61a80f25a3c',
            'premium': False,
            'title': 'Test Movie',
            'actors_names': [],
            'writers_names': [],
            'directors_names': [],
            'genres_names': [],
            'actors': [],
            'writers': [],
            'directors': [],
            'genres': [],
        },
        {
            'uuid': '93d538fe-1328-4b4c-a327-f61a80f20000',
            'premium': False,
            'title': 'Dummy Movie',
            'actors_names': [],
            'writers_names': [],
            'directors_names': [],
            'genres_names': [],
            'actors': [],
            'writers': [],
            'directors': [],
            'genres': [],
        },
    ]
    await asyncio.gather(
        *[es_client.index('movies', body=film, id=film['uuid'], refresh='wait_for') for film in
          films])
    return films

# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_person_list(make_get_request, es_client: AsyncElasticsearch,
                           persons: List):
    response = await make_get_request('/person')
    assert response.status == 200
    assert len(response.body) == 3

# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_person_search(make_get_request, es_client: AsyncElasticsearch,
                             persons: List):
    # Единственное совпадение
    response = await make_get_request('/person', {'query': 'Chris'})
    assert response.status == 200
    assert len(response.body) == 1
    assert response.body[0]['uuid'] == '0040371d-f875-4d42-ab17-ffaf3cacfb91'
    assert response.body[0]['full_name'] == 'Chris Cooper'
    assert response.body[0]['roles'] == ["actor"]

    # Несколько совпадений
    response = await make_get_request('/person', {'query': 'June'})
    assert response.status == 200
    assert len(response.body) == 2
    expected_person_ids = {persons[1]['uuid'], persons[2]['uuid']}
    assert response.body[0]['uuid'] in expected_person_ids
    assert response.body[1]['uuid'] in expected_person_ids

    # Лучшее совпадение
    response = await make_get_request('/person', {'query': 'June Laverick2'})
    assert response.status == 200
    assert len(response.body) == 2
    assert response.body[0]['uuid'] == '0040371d-f875-4d42-ab17-ffaf3cacfb92'
    assert response.body[0]['full_name'] == 'June Laverick2'

# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_person_search_paginated_and_limited_result(make_get_request,
                                                          es_client: AsyncElasticsearch,
                                                          persons: List):
    response = await make_get_request('/person', {'page[size]': 2})
    assert response.status == 200
    assert len(response.body) == 2

    response = await make_get_request('/person', {'page[size]': 2, 'page[number]': 2})
    assert response.status == 200
    assert len(response.body) == 1

    response = await make_get_request('/person', {'page[size]': -1})
    assert response.status == 422

    response = await make_get_request('/person', {'page[size]': 2, 'page[number]': 4444})
    assert response.status == 404

# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_person_search_sorted_result(make_get_request, es_client: AsyncElasticsearch,
                                           persons: List):
    response = await make_get_request('/person', {'sort': 'incorrect_sort'})
    assert response.status == 400

    response = await make_get_request('/person', {'sort': '-full_name'})
    assert response.status == 200
    assert len(response.body) == 3
    result_persons = [person['full_name'] for person in response.body]
    expected_persons = sorted([person['full_name'] for person in persons], reverse=True)
    assert result_persons == expected_persons

# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_person_search_not_found(make_get_request, es_client: AsyncElasticsearch, persons: List):
    response = await make_get_request('/person', {'query': 'Something'})
    assert response.status == 404

# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_person_detail(make_get_request, es_client: AsyncElasticsearch, persons: List):
    lookup_person_id = persons[0]['uuid']
    person_detail_endpoint = f'/person/{lookup_person_id}'
    response = await make_get_request(person_detail_endpoint)

    assert response.status == 200
    assert response.body['uuid'] == '0040371d-f875-4d42-ab17-ffaf3cacfb91'
    assert response.body['full_name'] == 'Chris Cooper'
    assert response.body['roles'] == ["actor"]

# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_person_detail_not_found(make_get_request, es_client: AsyncElasticsearch, persons: List):
    person_detail_endpoint = '/person/1'
    response = await make_get_request(person_detail_endpoint)

    assert response.status == 404

# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_person_films(make_get_request, es_client: AsyncElasticsearch,
                            person_movies: List, persons: List):
    # Один фильм
    lookup_person_id = persons[0]['uuid']
    person_film_endpoint = f'/person/{lookup_person_id}/film'
    response = await make_get_request(person_film_endpoint)

    assert response.status == 200
    assert len(response.body) == 1
    assert response.body[0]['uuid'] == "93d538fe-1328-4b4c-a327-f61a80f25a3c"
    assert response.body[0]['title'] == 'Test Movie'

    # Несколько фильмов
    lookup_person_id = persons[1]['uuid']
    person_film_endpoint = f'/person/{lookup_person_id}/film'
    response = await make_get_request(person_film_endpoint)

    expected_film_ids = {person_movies[0]['uuid'], person_movies[1]['uuid']}

    assert response.status == 200
    assert len(response.body) == 2
    assert response.body[0]['uuid'] in expected_film_ids
    assert response.body[1]['uuid'] in expected_film_ids

    # Ни одного фильма
    lookup_person_id = persons[2]['uuid']
    person_film_endpoint = f'/person/{lookup_person_id}/film'
    response = await make_get_request(person_film_endpoint)

    assert response.status == 404

# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_redis_cache(make_get_request, redis: Redis, persons: List):
    await redis.flushall()
    assert not (await redis.keys("Person:query:*"))
    response = await make_get_request('/person', {'query': 'Chris'})

    assert response.status == 200
    assert await redis.keys("Person:query:*")
