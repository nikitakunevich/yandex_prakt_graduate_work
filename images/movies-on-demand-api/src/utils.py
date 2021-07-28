"""Модуль содержит вспомогательные функции."""
from typing import Optional

import httpx
import jwt
from fastapi import HTTPException

from config import settings
from models import Movie


def is_premium_user(token: str) -> bool:
    """Проверяет оформил ли подписку пользователь."""
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = token.removeprefix("Bearer ")
    payload = jwt.decode(token, key=settings.auth_public_key, algorithms=["RS256"])
    return bool(payload["prm"])


def get_movie_by_id(movie_id: str, auth_token: Optional[str] = None) -> Movie:
    """Возвращает информацию о фильме по id."""

    url = f"http://{settings.search_api_host}/v1/private/film/{movie_id}"
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else None
    resp = httpx.get(url, headers=headers)

    if resp.is_error:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"From search_api private/film/<id>: {resp.text}",
        )

    return Movie(**resp.json())
