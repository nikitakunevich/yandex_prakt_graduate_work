"""Модуль содержит настройки."""
from pathlib import Path

from pydantic import BaseSettings

BASE_PATH = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Общий класс настроек."""

    log_level: str = "INFO"
    cf_key_id: str
    cf_domain_name: str
    cf_private_key_file: str
    url_path_prefix: str
    url_expire_hours: int
    search_api_host: str
    pytest_debug: bool = False

    @property
    def auth_public_key(self) -> str:
        """Возвращает ключ с помощью которого закодирован JWT."""
        value = self.__dict__.get("auth_public_key")
        if value is None:
            with open(BASE_PATH.joinpath("rs256.pub"), "r") as file:
                value = file.read()
        return value


settings = Settings()
