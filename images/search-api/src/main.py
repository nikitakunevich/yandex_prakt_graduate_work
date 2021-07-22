import logging.config

import defaults
import jwt
import uvicorn as uvicorn
from api_v1 import film, genre, person
from config import config
from db import cache, elastic
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.authentication import AuthenticationMiddleware
from auth import JWTAuthBackend

app = FastAPI(
    title="Films API",
    docs_url="/swagger",
    openapi_url="/swagger.json",
    default_response_class=ORJSONResponse,
)
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())


@app.on_event("startup")
async def startup():
    logging.config.dictConfig(defaults.LOGGING)

    await cache.get_cache_storage()
    elastic.es = AsyncElasticsearch(config.ES_URL)


@app.on_event("shutdown")
async def shutdown():
    await cache.cache.close()
    await elastic.es.close()


@app.get('/health-check')
def health_check():
    return {'status': 'healthy'}


app.include_router(film.router, prefix="/v1/film", tags=["film"])
app.include_router(person.router, prefix="/v1/person", tags=["person"])
app.include_router(genre.router, prefix="/v1/genre", tags=["genre"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=defaults.LOGGING,
        log_level=logging.DEBUG,
    )
