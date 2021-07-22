import logging
from typing import List, Optional
from uuid import UUID

from api_v1.constants import FILM_NOT_FOUND, PERSON_NOT_FOUND
from api_v1.models import FilmShort, Person
from fastapi import APIRouter, Depends, HTTPException, Query, status
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service
from starlette.requests import Request
from utils import can_read_premium

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{person_id:uuid}", response_model=Person)
async def person_details(
    person_id: UUID, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(str(person_id))
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PERSON_NOT_FOUND
        )

    return Person.from_db_model(person)


@router.get("/", response_model=List[Person])
async def person_search(
    query: Optional[str] = Query(""),
    sort: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$"),
    page_number: int = Query(1, alias="page[number]", gt=0),
    page_size: int = Query(50, alias="page[size]", gt=0),
    person_service: PersonService = Depends(get_person_service),
) -> List[Person]:
    persons = await person_service.search(
        search_query=query, sort=sort, page_size=page_size, page_number=page_number
    )
    if not persons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PERSON_NOT_FOUND
        )

    return [Person.from_db_model(person) for person in persons]


@router.get("/{person_id:uuid}/film", response_model=List[FilmShort])
async def person_films(
    request: Request,
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmShort]:
    person = await person_service.get_by_id(str(person_id))
    person_films = await film_service.bulk_get_by_ids(
        person.film_ids, filter_premium=not can_read_premium(request.auth)
    )
    if not person_films:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=FILM_NOT_FOUND
        )

    return [FilmShort.from_db_model(film) for film in person_films]
