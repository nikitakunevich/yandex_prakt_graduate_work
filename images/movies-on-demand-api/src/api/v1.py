import logging

import jwt
from fastapi import APIRouter, HTTPException, Request

from exceptions import MissingMovieFileError, MissingSubscriptionError
from models import MovieIDRequest
from url_signer import get_signed_url
from utils import get_movie_by_id, is_premium_user

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/health-check")
async def health_check() -> dict[str, str]:
    """Проверка состояния сервиса."""
    return {"status": "healthy"}


@router.post("/movie_private_link", status_code=200)
async def create_private_link(
    movie_id_request: MovieIDRequest, request: Request
) -> dict[str, str]:
    """Создает ссылку для доступа к фильму."""

    try:
        token = request.headers.get("Authorization")
        premium_user = is_premium_user(token)

        logger.debug("Getting movie metadata")
        movie = await get_movie_by_id(str(movie_id_request.id), auth_token=token)

        if not movie.filename:
            raise MissingMovieFileError()
        if movie.premium and not premium_user:
            raise MissingSubscriptionError()

        url = get_signed_url(movie.filename)
        return {"url": url}

    except jwt.exceptions.ExpiredSignatureError as exc:
        raise HTTPException(status_code=400, detail="Expired token") from exc
