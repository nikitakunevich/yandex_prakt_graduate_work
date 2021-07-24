import logging
from uuid import UUID

from api_v1 import constants
from api_v1.models import PrivateFilmDetails
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.authentication import AuthenticationError

from auth import Permissions
from services.film import FilmService, get_film_service
from starlette.requests import Request
from utils import can_read_premium

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/film/{film_id:uuid}", response_model=PrivateFilmDetails)
async def get_private_film_details(
        request: Request,
        film_id: UUID,
        film_service: FilmService = Depends(get_film_service),
) -> PrivateFilmDetails:
    if Permissions.filename_read not in request.auth.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=constants.PRIVATE_FILM_NO_RIGHTS)

    film = await film_service.get_by_id(
        str(film_id), filter_premium=not can_read_premium(request.auth)
    )
    logger.debug(f"got {film=}")
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=constants.FILM_NOT_FOUND
        )

    return PrivateFilmDetails.from_db_model(film)