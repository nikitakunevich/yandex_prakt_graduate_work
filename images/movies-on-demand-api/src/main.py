import logging
from typing import Optional

import jwt
import time

from fastapi import FastAPI, HTTPException, Request
import httpx
from httpx import HTTPStatusError

from config import settings
from models import Movie, MovieIDRequest
from url_signer import get_signed_url

app = FastAPI()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class MissingSubscriptionError(Exception):
    pass

class MissingMovieFileError(Exception):
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


def get_movie_by_id(movie_id: str, auth_token: Optional[str] = None) -> Optional[dict]:
    """Возвращает информацию о фильме по id."""

    url = f"http://{settings.search_api_host}/v1/private/film/{movie_id}"
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else None
    resp = httpx.get(url, headers=headers)
    try:
        resp.raise_for_status()
    except HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"From search_api private/film/<id>: {exc.response.text}"
        ) from exc
    json_resp = resp.json()
    print(json_resp)
    return json_resp


@app.post("/api/v1/movie_private_link", status_code=201)
def create_private_link(movie_id_request: MovieIDRequest, request: Request) -> dict:
    """Создает ссылку для доступа к фильму."""

    try:
        # decode token data

        token = request.headers.get("Authorization", None)
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized")
        token = token.removeprefix("Bearer ")
        print(token)
        payload = jwt.decode(token, key=settings.auth_public_key, algorithms=['RS256'])
        print(payload)
        is_premium_user = payload['prm']
        token_expire_time = payload['exp']
        if time.time() > token_expire_time:
            raise Exception('Your token has expired')
        logger.debug("get_movie_metadata")
        # get movie metadata
        movie = get_movie_by_id(movie_id_request.id, auth_token=token)
        movie = Movie(**movie)
        if not movie.filename:
            raise MissingMovieFileError
        if movie.premium and not is_premium_user:
            raise MissingSubscriptionError

        url = get_signed_url(movie.filename)

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
    except MissingMovieFileError as exc:
        raise HTTPException(
            status_code=404,
            detail="No existing video file for movie"
        ) from exc
    except HTTPException as exc:
        raise exc from exc
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
