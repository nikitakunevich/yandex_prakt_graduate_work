from pydantic import BaseSettings


class Settings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = 6379
    CACHE_TTL: int = 60 * 5

    # Настройки Elasticsearch
    ES_URL: str = "http://127.0.0.1:9200"

    LOG_LEVEL: str = "WARNING"

    JWT_PUBLIC_KEY: str
    JWT_ALGORITHM: str = "RS256"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()
