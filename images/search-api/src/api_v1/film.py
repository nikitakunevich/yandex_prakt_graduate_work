import logging
from typing import List, Optional
from uuid import UUID

from api_v1.constants import FILM_NOT_FOUND
from api_v1.models import FilmDetails, FilmShort
from fastapi import APIRouter, Depends, HTTPException, Query, status
from services.film import FilmService, get_film_service
from starlette.requests import Request
from utils import can_read_premium

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{film_id:uuid}", response_model=FilmDetails)
async def film_details(
    request: Request,
    film_id: UUID,
    film_service: FilmService = Depends(get_film_service),
) -> FilmDetails:
    film = await film_service.get_by_id(
        str(film_id), filter_premium=not can_read_premium(request.auth)
    )
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=FILM_NOT_FOUND
        )

    return FilmDetails.from_db_model(film)


@router.get("/", response_model=List[FilmShort])
async def film_search(
    request: Request,
    query: Optional[str] = Query(""),
    filter_genre: Optional[UUID] = Query(None, alias="filter[genre]"),
    sort: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$"),
    page_number: int = Query(1, alias="page[number]", gt=0),
    page_size: int = Query(50, alias="page[size]", gt=0),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmShort]:
    logger.debug(f"search sort: {sort}")
    films = await film_service.search(
        search_query=query,
        sort=sort,
        page_size=page_size,
        page_number=page_number,
        genre_filter=str(filter_genre) if filter_genre else None,
        filter_premium=not can_read_premium(request.auth),
    )
    if not films:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=FILM_NOT_FOUND
        )

    return [FilmShort.from_db_model(film) for film in films]
