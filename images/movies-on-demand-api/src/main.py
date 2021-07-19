import logging
import jwt
import time

from fastapi import FastAPI, HTTPException, Request

from config import settings
from models import Movie, MovieIDRequest
from url_signer import get_signed_url

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)


class MissingSubscriptionError(Exception):
    pass


@app.on_event("startup")
def init():
    logger.info('Starting application.\n')
    for param in settings.__dict__:
        if settings.__dict__[param] is None:
            raise Exception(f'Configuration parameter {param} is not set.')
        logger.info(f'{param} = {settings.__dict__[param]}')


@app.on_event("shutdown")
def shutdown():
    logger.info('Shutting down.\n')


def get_movie_by_id(_) -> dict:
    """Возвращает информацию о фильме по id."""
    return {
        "id": "93a9fe05-a816-422d-97e0-6e8f718b0027",
        "name": "Rainbow",
        "is_premium": True,
        "file_name": "girl-showing-rainbow.mp4",
    }


@app.post("/api/v1/movie_private_link", status_code=201)
def create_private_link(movie_id_request: MovieIDRequest, request: Request) -> dict:
    """Создает ссылку для доступа к фильму."""

    try:
        # decode token data
        token = request.headers.get("Authorization", None).removeprefix("Bearer ")
        print(token)
        payload = jwt.decode(token, key=settings.auth_public_key, algorithms=['RS256'])
        print(payload)
        is_premium_user = payload['prm']
        token_expire_time = payload['exp']
        if time.time() > token_expire_time:
            raise Exception('Your token has expired')

        # get movie metadata
        movie = get_movie_by_id(movie_id_request.id)
        movie = Movie(**movie)

        if movie.is_premium and not is_premium_user:
            raise MissingSubscriptionError

        url = get_signed_url(movie.file_name)

    except jwt.exceptions.ExpiredSignatureError as exc:
        logger.exception(exc)
        raise HTTPException(
            status_code=400,
            detail="400: Expired token",
        ) from exc

    except MissingSubscriptionError as exc:
        logger.exception(exc)
        raise HTTPException(
            status_code=403,
            detail="403: Missing subscription",
        ) from exc

    except Exception as exc:
        logger.exception(exc)
        raise HTTPException(
            status_code=500,
            detail="500: Internal error",
        ) from exc

    return {"url": url}


@app.get("/health-check")
def health_check():
    return {"status": "healthy"}
