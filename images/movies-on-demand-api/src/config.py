"""Модуль содержит настройки."""
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Общий класс настроек."""

    log_level: str = "INFO"
    cf_key_id: str
    cf_domain_name: str
    cf_private_key_file: str
    url_path_prefix: str
    url_expire_hours: int
    search_api_host: str

    @property
    def auth_public_key(self) -> str:
        """Возвращает ключ с помощью которого закодирован JWT."""
        value = self.__dict__.get("auth_public_key")
        if value is None:
            with open("rs256.pub", "rb") as file:
                value = file.read().decode()
        return value


settings = Settings()
