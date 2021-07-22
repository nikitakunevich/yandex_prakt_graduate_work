import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import aiohttp
import aioredis
import pytest
from aioredis.commands import Redis
from db.models import Film
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from .settings import Settings


@pytest.fixture(scope='session')
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def redis(settings) -> Redis:
    redis_host, redis_port = settings.REDIS_SOCKET.split(":")

    redis = await aioredis.create_redis_pool((redis_host, redis_port), minsize=10, maxsize=20)
    await redis.flushall()
    yield redis
    redis.close()
    await redis.wait_closed()


@pytest.fixture(scope='session')
async def es_client(settings):
    async def create_indices(indx_name, schema_path):
        return await client.indices.create(indx_name, body=json.load(open(schema_path)))

    async def delete_indices(indx_name):
        await client.indices.delete(indx_name)

    def get_schema_path(name):
        return str(Path(__file__).parent.parent.parent / 'schemas' / f'es.{name}.schema.json')

    index_names = ['movies', 'genres', 'persons']
    client = AsyncElasticsearch(hosts=settings.es_url)
    try:
        await asyncio.gather(*[delete_indices(name) for name in index_names])
    except Exception:
        pass

    await asyncio.gather(*[create_indices(index, get_schema_path(index)) for index in index_names])

    yield client

    await asyncio.gather(*[delete_indices(name) for name in index_names])
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture
def make_get_request(session, settings):
    async def inner(method: str, params: dict = None, headers: dict = None) -> HTTPResponse:
        params = params or {}
        url = settings.api_host + '/v1' + method  # в боевых системах старайтесь так не делать!
        async with session.get(url, params=params, headers = headers or {}) as response:
            body = await response.json()
            return HTTPResponse(
                body=body,
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture
@pytest.mark.asyncio
async def make_group_get_request(make_get_request):
    async def inner(urls: list) -> list[HTTPResponse]:
        requests = [make_get_request(url) for url in urls]
        return cast(list[HTTPResponse], await asyncio.gather(*requests))

    return inner
