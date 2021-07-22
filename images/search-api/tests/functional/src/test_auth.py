import asyncio
from operator import attrgetter

from aioredis import Redis
import pytest

import db.models
from api_v1.models import FilmShort, FilmDetails
import pydantic

from db.models import Film

API_URL = '/film/'

ADMIN_ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MCwianRpIjoiZDU4ZTZhMjktMTAxMy00YjhjLWI4YzYtMjZiM2JhM2VlZDQyIiwibmJmIjowLCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoiNzA2NmVmMjctMGQ5NS00MzVjLTg4MGYtNWZiYTQzOWFlZDczIiwiZXhwIjo5OTk5OTk5OTk5LCJwZXJtaXNzaW9ucyI6WyJyb2xlOndyaXRlIiwic3VzcGljaW91czpyZWFkIl0sImRldmljZSI6InRlc3R1c2VyIn0.Yfe944S7-mTbn3Y-8NrMz8Ln8HCQc67R-7k_goL0djhRC1ygI9ltewj8lnR7BvVZl1T3cbw6kIX-7-IMS3hy4vQ2HVYvpCKUQ7nPiFJ7FTxu8p71-QmDqZ1mOCvwYKO_Xm4I_e9kY0qE97a_IoL2iD1p90q0IAXuHStU9Mqxn9Tc9NS1BtdfmXforZHPG5tjQhOwdWG9tPjIbJOS783guOjdFu9MfFinmrSW4to4D29KNiTFsQ-jw33ZyAvQf7ii5ae817vno17k7hY5Y2hYEpkbxrbgQdqmVAWpujELsq06ecFFfitX0yjsr6fwbNeYthDqw2Np41uho2bXIz42pQ'
USER_ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MCwianRpIjoiZDU4ZTZhMjktMTAxMy00YjhjLWI4YzYtMjZiM2JhM2VlZDQyIiwibmJmIjowLCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoiNzA2NmVmMjctMGQ5NS00MzVjLTg4MGYtNWZiYTQzOWFlZDczIiwiZXhwIjo5OTk5OTk5OTk5LCJwZXJtaXNzaW9ucyI6WyJzdXNwaWNpb3VzOnJlYWQiXSwiZGV2aWNlIjoidGVzdHVzZXIifQ.DSrEz8ktEC_ib_00daEvdBTgVwunjzB7K7F0g2P7kAjxjRe_jxYKt5Wl7Idi9fHHqCWROJKneYdnpFHgl99A5Fs8XlgRHig3hHSHkVA7ajN2RXTYbIgrV-K81K9YnAvgHTaoH_ZYFJpUDAUh6cOoslgp3piD-xsk3FYPlzAt1VNFHWgiPEHBBLUj1xFfFozm7FSeBepJXRb01RN6a7m7pG0JqVxb4viybxoAmVttTk9_tn8Ev26x936SIXEnZWhdnulM5NJO6TF51eBN0FYLs5IRvUKdrBDjIc8CEF19mHXdSERyAPD4V3KGu8KYN0GjaDHEwrcXMQNsxB8YBNNBpg'


@pytest.fixture
async def films(es_client):
    # Заполнение данных для теста

    # 2 фильма Star Wars, 2 фильма Star Trek
    test_films = [
        {
            "imdb_rating": 6.2,
            "premium": True,
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
            "imdb_rating": 3.2,
            "premium": True,

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
        *[es_client.index('movies', body=film, id=film['uuid'], refresh='wait_for') for film in test_films])

    return test_films


# Пытаюсь получить фильмы будучи unauth —> получаю только 5+ рейтинг
#

@pytest.mark.asyncio
async def test_unauth_get_only_unpremium(make_get_request, films):
    expected_films = [film for film in films if not film["premium"]]
    expected_films = pydantic.parse_obj_as(list[FilmShort], expected_films)
    film_response = await make_get_request(API_URL)
    assert film_response.status == 200
    assert sorted(expected_films, key=attrgetter('uuid')) == sorted(
        pydantic.parse_obj_as(list[FilmShort], film_response.body), key=attrgetter('uuid'))


# Пытаюсь получить фильмы будучи auth -> в выдаче есть 0+ рейтинг

@pytest.mark.asyncio
async def test_auth_get_all_movies(make_get_request, films):
    expected_films = pydantic.parse_obj_as(list[FilmShort], films)
    film_response = await make_get_request(API_URL,
                                           headers={"Authorization": f"Bearer {USER_ACCESS_TOKEN}"})

    assert film_response.status == 200
    assert sorted(expected_films, key=attrgetter('uuid')) == sorted(
        pydantic.parse_obj_as(list[FilmShort], film_response.body), key=attrgetter('uuid'))


@pytest.mark.asyncio
async def test_unauth_get_premium_movie_failure(make_get_request, films):
    film_response = await make_get_request(f'{API_URL}fff4777b-7fe5-4be9-a6ea-6acb75b96fb0')
    assert film_response.status == 404


@pytest.mark.asyncio
async def test_auth_get_premium_movie_success(make_get_request, films):
    expected_film = [film for film in films if film['uuid'] == 'fff4777b-7fe5-4be9-a6ea-6acb75b96fb0'][0]
    expected_film = FilmDetails.from_db_model(db.models.Film.parse_obj(expected_film))
    film_response = await make_get_request(f'{API_URL}fff4777b-7fe5-4be9-a6ea-6acb75b96fb0',
                                           headers={"Authorization": f"Bearer {USER_ACCESS_TOKEN}"})
    assert film_response.status == 200
    assert expected_film == pydantic.parse_obj_as(FilmDetails, film_response.body)
