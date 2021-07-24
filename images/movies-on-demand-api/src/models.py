"""Содержит модели для работы с данными."""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class MovieIDRequest(BaseModel):
    """Применяется для валидации при запросе."""
    id: UUID


class Movie(BaseModel):
    """Экземпляр фильма."""
    uuid: str
    title: str
    filename: Optional[str]
    premium: bool
