"""Содержит модели для работы с данными."""
from uuid import UUID

from pydantic import BaseModel


class MovieIDRequest(BaseModel):
    """Применяется для валидации при запросе."""
    id: UUID


class Movie(BaseModel):
    """Экземпляр фильма."""
    id: UUID
    name: str
    file_name: str
    is_premium: bool
