import logging
from typing import List, Optional
from uuid import UUID

from api_v1.constants import FILM_NOT_FOUND, GENRE_NOT_FOUND
from api_v1.models import FilmShort, Genre, GenreDetail
from fastapi import APIRouter, Depends, HTTPException, Query, status
from services.film import FilmService, get_film_service
from services.genre import GenreService, get_genre_service
from starlette.requests import Request
from utils import can_read_premium

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[Genre])
async def genres_all(
    query: Optional[str] = Query(""),
    sort: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$"),
    page_number: int = Query(1, alias="page[number]"),
    page_size: int = Query(50, alias="page[size]"),
    genre_service: GenreService = Depends(get_genre_service),
) -> List[Genre]:
    genres = await genre_service.search(
        search_query=query, sort=sort, page_size=page_size, page_number=page_number
    )
    if not genres:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=GENRE_NOT_FOUND
        )

    return [Genre.from_db_model(genre) for genre in genres]


@router.get("/{genre_id:uuid}", response_model=GenreDetail)
async def genre_detail(
    genre_id: UUID, genre_service=Depends(get_genre_service)
) -> GenreDetail:
    genre = await genre_service.get_by_id(str(genre_id))
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=GENRE_NOT_FOUND
        )
    return GenreDetail.from_db_model(genre)


@router.get("/{genre_id:uuid}/genre", response_model=List[FilmShort])
async def genre_films(
    request: Request,
    genre_id: UUID,
    genre_service: GenreService = Depends(get_genre_service),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmShort]:
    genre = await genre_service.get_by_id(str(genre_id))
    genre_films = await film_service.bulk_get_by_ids(
        genre.film_ids, filter_premium=not can_read_premium(request.auth)
    )
    if not genre_films:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=FILM_NOT_FOUND
        )

    return [FilmShort.from_db_model(film) for film in genre_films]
