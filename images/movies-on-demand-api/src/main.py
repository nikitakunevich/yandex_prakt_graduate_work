import logging
import jwt
from fastapi import FastAPI, HTTPException, Request

from config import settings
from exceptions import MissingMovieFileError, MissingSubscriptionError, raise_http_exception
from models import Movie, MovieIDRequest
from url_signer import get_signed_url
from utils import check_user_subscription, get_movie_by_id

app = FastAPI()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


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


@app.get("/health-check")
def health_check():
    return {"status": "healthy"}


@app.post("/api/v1/movie_private_link", status_code=201)
def create_private_link(movie_id_request: MovieIDRequest, request: Request) -> dict:
    """Создает ссылку для доступа к фильму."""

    try:
        token = request.headers.get("Authorization", None)
        is_premium_user = check_user_subscription(token)

        logger.debug("Getting movie metadata")
        movie = get_movie_by_id(movie_id_request.id, auth_token=token)
        movie = Movie(**movie)

        if not movie.filename:
            raise MissingMovieFileError
        if movie.premium and not is_premium_user:
            raise MissingSubscriptionError

        url = get_signed_url(movie.filename)
        return {"url": url}

    except jwt.exceptions.ExpiredSignatureError as exc:
        raise_http_exception(exc, logger, 400, "Expired token")

    except MissingSubscriptionError as exc:
        raise_http_exception(exc, logger, 403, "Missing subscription")

    except MissingMovieFileError as exc:
        raise_http_exception(exc, logger, 404, "No existing video file for movie")

    except HTTPException as exc:
        raise_http_exception(exc, logger, exc.status_code, exc.detail)

    except Exception as exc:
        raise_http_exception(exc, logger, 500, "Internal error")

