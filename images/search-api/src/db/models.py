from typing import List, Optional

from pydantic import BaseModel

ObjectId = str
ObjectName = str


class IdName(BaseModel):
    uuid: str
    name: str


class BaseESModel(BaseModel):
    uuid: str


class Film(BaseESModel):
    imdb_rating: Optional[float]
    title: str
    description: Optional[str]

    actors_names: List[str]
    writers_names: List[str]
    directors_names: List[str]
    genres_names: List[str]
    actors: List[IdName]
    writers: List[IdName]
    directors: List[IdName]
    genres: List[IdName]


class FilmShort(BaseESModel):
    title: str
    imdb_rating: Optional[float]


class Genre(BaseESModel):
    name: str
    film_ids: List[str]


class Person(BaseESModel):
    full_name: str
    roles: List[str]
    film_ids: List[str]
