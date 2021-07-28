"""Основной модуль приложения."""
import logging

import jwt
from fastapi import FastAPI, HTTPException, Request

from config import settings
from exceptions import MissingMovieFileError, MissingSubscriptionError
from models import MovieIDRequest
from url_signer import get_signed_url
from utils import get_movie_by_id, is_premium_user

app = FastAPI()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
def shutdown() -> None:
    """Триггер событий после завершения работы."""
    logger.info("Shutting down.\n")


@app.get("/health-check")
def health_check() -> dict[str, str]:
    """Проверка состояния сервиса."""
    return {"status": "healthy"}


@app.post("/api/v1/movie_private_link", status_code=201)
def create_private_link(
    movie_id_request: MovieIDRequest, request: Request
) -> dict[str, str]:
    """Создает ссылку для доступа к фильму."""

    try:
        token = request.headers.get("Authorization")
        premium_user = is_premium_user(token)

        logger.debug("Getting movie metadata")
        movie = get_movie_by_id(str(movie_id_request.id), auth_token=token)

        if not movie.filename:
            raise MissingMovieFileError()
        if movie.premium and not premium_user:
            raise MissingSubscriptionError()

        url = get_signed_url(movie.filename)
        return {"url": url}

    except jwt.exceptions.ExpiredSignatureError as exc:
        raise HTTPException(status_code=400, detail="Expired token") from exc

    except MissingSubscriptionError as exc:
        raise HTTPException(status_code=403, detail="Missing subscription") from exc

    except MissingMovieFileError as exc:
        raise HTTPException(
            status_code=404, detail="No existing video file for movie"
        ) from exc

    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    except Exception as exc:  # pylint: disable=W0703
        raise HTTPException(status_code=500, detail="Internal error") from exc
