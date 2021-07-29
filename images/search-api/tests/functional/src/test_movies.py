import asyncio

from aioredis import Redis
import pytest
from api_v1.models import FilmShort, FilmDetails
from db.models import Film

API_URL = '/film/'


@pytest.fixture
async def films(es_client):
    # Заполнение данных для теста

    # 2 фильма Star Wars, 2 фильма Star Trek
    test_films = [
        {
            "imdb_rating": 8.1,
            "premium": False,
            "uuid": "fff4777b-7fe5-4be9-a6ea-6acb75b96fb0",
            "title": "Star Wars: The Old Republic - Rise of the Hutt Cartel",
            "description": "With the Sith emperor defeated, the republic & empire grow ever more desperate to win the conflict. All eyes turn on the planet Makeb, where a mysterious substance called isotope-5 has been discovered. This substance has the power to fuel a massive army for whoever wields it. Unfortunately for both sides, the hutt cartel has control of the planet, and will not give it up lightly...",
            "actors_names": ["a", "aa"],
            "writers_names": ["w", "ww"],
            "directors_names": ["d"],
            "genres_names": ["Action"],
            "actors": [
            ],
            "writers": [
                {
                    "uuid": "279842e9-28f3-49f4-9914-46f8b4ad92c9",
                    "name": "w"
                },
            ],
            "directors": [
                {
                    "uuid": "f87486ec-7682-407b-8346-23947d944820",
                    "name": "d"
                }
            ],
            "genres": [
                {
                    "uuid": "6ae86dab-dbc2-478c-9151-ddfd8c92c10a",
                    "name": "Action"
                }
            ]
        },
        {
            "imdb_rating": 7.1,
            "premium": False,
            "uuid": "fdaf4660-6456-4e99-8009-c9e0db67ea90",
            "title": "Star Wars: The New Republic Anthology",
            "description": "Boba Fett has been trapped for 30 years in the Great Pit of Carkoon; makes his escape and is now allies with the Rebellion.",
            "actors_names": ["a2", "aa2"],
            "writers_names": ["w2", "ww2"],
            "directors_names": ["d2", "dd2"],
            "genres_names": ["Thriller"],
            "actors": [
                {
                    "uuid": "929d9e18-f5d1-4198-97b2-4e2ddbe28f76",
                    "name": "a2"
                },
                {
                    "uuid": "620a94fe-f76e-4a0e-b6c9-f8f7c14d811d",
                    "name": "aa2"
                }
            ],
            "writers": [
                {
                    "uuid": "845de5a7-b57f-42a2-a2d1-ad07d88e1689",
                    "name": "w2"
                },
                {
                    "uuid": "bb871757-9e79-4bd6-978c-a683ae0c127c",
                    "name": "ww2"
                }
            ],
            "directors": [
                {
                    "uuid": "8a2b3048-d9b7-4874-9ef5-cb9155b9fc38",
                    "name": "dd2"
                }
            ],
            "genres": [
                {
                    "uuid": "9a09f1b3-a3f8-4939-b175-29beeba1a6b3",
                    "name": "Thriller"
                }
            ]
        },
        {
            "imdb_rating": 5.7,
            "premium": False,
            "uuid": "fdfc8350-4ec4-45c5-9ce9-9139c3e2fce6",
            "title": "Star Trek: Horizon",
            "description": "In a time prior to the United Federation of Planets, a young coalition of worlds led by Earth battle the Romulan Star Empire for their very survival.",
            "actors_names": ["a3", "aa3"],
            "writers_names": ["w3", "ww3"],
            "directors_names": ["d3"],
            "genres_names": ["War"],
            "actors": [
                {
                    "uuid": "84df81ae-7845-4d78-963e-47b0a8a4b972",
                    "name": "aa3"
                }
            ],
            "writers": [
                {
                    "uuid": "2ee03ec0-ea75-42f5-841e-189ad7aadd72",
                    "name": "ww3"
                }
            ],
            "directors": [
                {
                    "uuid": "45cbadba-a15d-4036-87e8-a64e749f0ad8",
                    "name": "d3"
                }
            ],
            "genres": [
                {
                    "uuid": "67ae3870-b50d-4508-b2a6-ade667149ceb",
                    "name": "War"
                }
            ]
        },
        {
            "imdb_rating": 7.5,
            "premium": False,
            "uuid": "fd7d8ea7-396a-42af-8b0a-ec2747e27506",
            "title": "Star Trek: Enterprise",
            "description": "The year is 2151. Earth has spent the last 88 years since learning how to travel faster than the speed of light studying under the wisdom of their alien ally called the 'Vulcans'. Now, the first crew of human explorers sets out into deep space on a ship called the 'Enterprise' to see what is beyond our solar system.",
            "actors_names": ["a4", "aa4"],
            "writers_names": ["w4", "ww4"],
            "directors_names": ["d4"],
            "genres_names": ["Mystery"],
            "actors": [
                {
                    "uuid": "80227dc8-3e00-4b41-a2e3-350baacd9acb",
                    "name": "a4"
                }
            ],
            "writers": [
                {
                    "uuid": "449b2581-7459-4ab4-b504-ef9b6244a816",
                    "name": "w4"
                },
            ],
            "directors": [
                {
                    "uuid": "b2a9534a-2f6b-4754-9bd2-be7ce2233b51",
                    "name": "d4"
                }
            ],
            "genres": [
                {
                    "uuid": "e86e1386-64d4-4e0c-9162-af3363082727",
                    "name": "Mystery"
                }
            ]
        }
    ]

    await asyncio.gather(
        *[es_client.index('movies', body=film, id=film["uuid"], refresh='wait_for') for film in test_films])

    return test_films


@pytest.mark.asyncio
async def test_find_one(make_get_request, films):
    expected_film = next(filter(lambda f: f["title"].find('Hutt Cartel') >= 0, films))
    expected_film = FilmShort.from_db_model(Film.parse_obj(expected_film))
    film_response = await make_get_request(API_URL, {'query': 'Hutt Cartel'})

    assert film_response.status == 200

    assert len(film_response.body) == 1
    assert expected_film == FilmShort.parse_obj(film_response.body[0])


@pytest.mark.asyncio
async def test_find_multiple_films(make_get_request, films):
    film1, film2 = films[2], films[3]
    response_films_star_trek = await make_get_request(API_URL, {'query': 'Trek'})

    assert response_films_star_trek.status == 200
    assert len(response_films_star_trek.body) == 2

    films_star_trek_es_ids = {f['uuid'] for f in response_films_star_trek.body}
    assert film1['uuid'] in films_star_trek_es_ids
    assert film2['uuid'] in films_star_trek_es_ids


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_filter_genre(make_get_request, films):
    response_films_star_trek = await make_get_request(
        API_URL,
        {'query': 'Trek', 'filter[genre]': '67ae3870-b50d-4508-b2a6-ade667149ceb'}
    )
    assert response_films_star_trek.status == 200
    assert len(response_films_star_trek.body) == 1


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_filter_unknown_genre(make_get_request, films):
    response_films_star_trek = await make_get_request(
        API_URL,
        {'query': 'Trek', 'filter[genre]': '80746937-2fc6-45d7-a3e6-a5854aa66092'}
    )
    assert response_films_star_trek.status == 404


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_invalid_genre_filter(make_get_request, films):
    response_films_star_trek = await make_get_request(API_URL, {'query': 'trek', 'filter[genre]': 1})
    assert response_films_star_trek.status == 422


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_invalid_sort(make_get_request, films):
    response_films_star_trek = await make_get_request(API_URL, {'query': 'trek', 'sort': 'S'})
    assert response_films_star_trek.status == 400


@pytest.mark.asyncio
async def test_sort_rating_desc_multiple(make_get_request, films):
    response_films_star_trek = await make_get_request(API_URL, {'query': 'trek', 'sort': '-imdb_rating'})
    assert response_films_star_trek.status == 200
    assert len(response_films_star_trek.body) == 2

    assert response_films_star_trek.body[0]['uuid'] == films[3]["uuid"]


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_paging_one_on_page(make_get_request, films):
    response_films_star_trek = await make_get_request(API_URL, {'query': 'Trek', 'page[size]': 1})
    assert response_films_star_trek.status == 200
    assert len(response_films_star_trek.body) == 1


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_paging_second_page(make_get_request, films):
    response_films_star_trek = await make_get_request(API_URL, {'query': 'Trek', 'page[size]': 1, 'page[number]': 2})
    assert response_films_star_trek.status == 200
    assert len(response_films_star_trek.body) == 1


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_paging_empty_page(make_get_request, films):
    response_films_star_trek = await make_get_request(API_URL, {'query': 'Trek', 'page[size]': 1, 'page[number]': 4})
    assert response_films_star_trek.status == 404
    assert 'detail' in response_films_star_trek.body


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_paging_invalid_page_size(make_get_request, films):
    response_films_star_trek = await make_get_request(API_URL, {'query': 'Trek', 'page[size]': -1})
    assert response_films_star_trek.status == 422


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_paging_invalid_page_size(make_get_request, films):
    response_films_star_trek = await make_get_request(API_URL, {'query': 'Trek', 'page[number]': -1})
    assert response_films_star_trek.status == 422


@pytest.mark.asyncio
async def test_all_search(make_get_request):
    response_films_star_trek = await make_get_request(API_URL, {'query': 'Star'})

    assert response_films_star_trek.status == 200
    assert len(response_films_star_trek.body) == 4


@pytest.mark.asyncio
async def test_search_not_found(make_get_request):
    response_not_found = await make_get_request(API_URL, {'query': 'NotFoundFilm'})

    assert response_not_found.status == 404
    assert 'detail' in response_not_found.body


@pytest.mark.asyncio
async def test_detailed_info(make_get_request, films):
    film_title = 'Star Wars: The New Republic Anthology'
    expected_film = next(filter(lambda f: f["title"] == film_title, films))
    expected_film = FilmDetails.from_db_model(Film.parse_obj(expected_film))

    response_film_star_wars = await make_get_request(f'{API_URL}{expected_film.uuid}')
    assert response_film_star_wars.status == 200
    received_film = FilmDetails.parse_obj(response_film_star_wars.body)

    assert received_film == expected_film


@pytest.mark.asyncio
async def test_get_film_unknown_id(make_get_request):
    response_not_found = await make_get_request('/film/6bcc7f85-9e5d-45a9-91ec-25903212c8b7')

    assert response_not_found.status == 404
    assert 'detail' in response_not_found.body


@pytest.mark.asyncio
async def test_get_film_invalid_id(make_get_request):
    response_not_found = await make_get_request('/film/-1')
    assert response_not_found.status == 404
    assert 'detail' in response_not_found.body


@pytest.mark.asyncio
async def test_redis_cache(make_get_request, redis: Redis):
    await redis.flushall()
    assert not (await redis.keys("Film:query:*:safe"))
    response = await make_get_request(API_URL, {'query': 'Trek'})

    assert response.status == 200
    assert await redis.keys("Film:query:*")
