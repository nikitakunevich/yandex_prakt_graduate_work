from typing import Optional
import jwt
import httpx
from httpx import HTTPStatusError
from fastapi import HTTPException
from config import settings


def check_user_subscription(token: str) -> bool:
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = token.removeprefix("Bearer ")
    payload = jwt.decode(token, key=settings.auth_public_key, algorithms=['RS256'])
    return bool(payload['prm'])


def get_movie_by_id(movie_id: str, auth_token: Optional[str] = None) -> Optional[dict]:
    """Возвращает информацию о фильме по id."""

    url = f"http://{settings.search_api_host}/v1/private/film/{movie_id}"
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else None
    resp = httpx.get(url, headers=headers)

    try:
        resp.raise_for_status()
    except HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"From search_api private/film/<id>: {exc.response.text}"
        ) from exc

    return resp.json()