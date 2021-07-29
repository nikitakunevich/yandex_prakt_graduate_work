"""Основной модуль приложения."""
import logging

import sentry_sdk

from fastapi import FastAPI

from api.v1 import router as v1_router
from config import settings

sentry_sdk.init(
    "https://6f0e6c17ccec41d6a58229df1c34b807@o828822.ingest.sentry.io/5883947",
    server_name="movies-on-demand-api",
    traces_sample_rate=1.0
)

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


def get_application() -> FastAPI:
    _app = FastAPI()

    @_app.on_event("shutdown")
    def shutdown() -> None:
        """Триггер событий после завершения работы."""
        logger.info("Shutting down.\n")

    _app.include_router(v1_router)
    return _app


app = get_application()
