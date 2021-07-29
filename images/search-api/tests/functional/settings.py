from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    es_url: str = Field('http://127.0.0.1:9200', env='ES_URL')
    api_host: str = Field('http://127.0.0.1:5000', env='API_HOST')
    REDIS_SOCKET: str = 'localhost:6379'
    log_level: str = Field('INFO', env='LOG_LEVEL')
