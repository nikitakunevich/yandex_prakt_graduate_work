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
    auth_public_key: str = open('rs256.pub', 'rb').read()
    search_api_host: str


settings = Settings()
