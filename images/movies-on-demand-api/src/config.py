"""Модуль содержит настройки."""
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Общий класс настроек."""
    log_level: str
    cf_key_id: str
    cf_domain_name: str
    cf_private_key_file: str
    url_path_prefix: str
    url_expire_hours: int


settings = Settings()
