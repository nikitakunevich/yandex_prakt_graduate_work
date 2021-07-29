import logging.config

import sentry_sdk

import defaults
import jwt
import uvicorn as uvicorn
from api_v1 import film, genre, person, private
from config import config
from db import cache, elastic
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.authentication import AuthenticationMiddleware
from auth import JWTAuthBackend

sentry_sdk.init(
    "https://6f0e6c17ccec41d6a58229df1c34b807@o828822.ingest.sentry.io/5883947",
    server_name="search-api",
    traces_sample_rate=1.0
)

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
app.include_router(private.router, prefix="/v1/private", tags=["private"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=defaults.LOGGING,
        log_level=logging.DEBUG,
    )
