import asyncio
import warnings

import pytest
from fastapi import FastAPI

from config import settings
from main import get_application


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return get_application()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()

    if settings.pytest_debug:
        loop.set_debug(True)  # Enable debug
        loop.slow_callback_duration = 0.001

        # Report all mistakes managing asynchronous resources.
        warnings.simplefilter("always", ResourceWarning)

    yield loop

    loop.close()
