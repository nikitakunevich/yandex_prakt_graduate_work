import dbm
from typing import Protocol

from redis import Redis

from postgres_to_es.utils import backoff


class State(Protocol):

    def state_set_key(self, key, value: str) -> None:
        ...

    def state_get_key(self, key, default: str = None) -> str:
        ...


class DBMState(State):
    def state_set_key(self, key, value: str) -> None:
        """Запись значения по ключу в dbm."""
        with dbm.open('state', 'c') as db:
            db[key] = value.encode()

    def state_get_key(self, key, default: str = None) -> str:
        """Чтение значения по ключу из dbm."""

        with dbm.open('state', 'c') as db:
            if default is not None:
                return db.setdefault(key, default.encode()).decode()

            return db[key].decode()


class RedisState:
    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    @backoff()
    def state_set_key(self, key, value: str) -> None:
        self.redis_adapter.set(key, value.encode())

    @backoff()
    def state_get_key(self, key, default: str = None) -> str:
        data = self.redis_adapter.get(key)
        if data:
            data = data.decode()
        else:
            self.state_set_key(key, default)
            data = default

        return data
