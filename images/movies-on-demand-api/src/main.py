import logging
from fastapi import FastAPI, HTTPException
from config import settings
from models import Movie, MovieIDRequest
from url_signer import get_signed_url

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)

CREATED = 201
NOT_FOUND = 404
INTERNAL_ERROR = 500


@app.on_event("startup")
def init():
    pass


@app.on_event("shutdown")
def shutdown():
    pass


def get_movie_by_id(movie_id):
    return {
        'id': '93a9fe05-a816-422d-97e0-6e8f718b0027',
        'name': 'Rainbow',
        'is_premium': True,
        'file_name': 'girl-showing-rainbow.mp4'
    }


@app.post("/api/v1/movie_private_link", status_code=CREATED)
def create_private_link(movie_id_request: MovieIDRequest):
    try:
        movie = get_movie_by_id(movie_id_request.id)
        movie = Movie(**movie)
        url = get_signed_url(movie.file_name)

    except Exception as err:
        logger.error("ERROR: " + str(err))
        raise HTTPException(
            INTERNAL_ERROR,
            detail="500: Internal server error. Please try later.",
        )

    return {"url": url}
