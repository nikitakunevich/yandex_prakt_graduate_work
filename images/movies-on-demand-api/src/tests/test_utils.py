import json
from uuid import uuid4

import pytest
from fastapi import HTTPException
from httpx import Response
from pytest_mock import MockFixture

from models import Movie
from utils import get_movie_by_id, is_premium_user


def test_is_premium_user(mocker: MockFixture):
    mocker.patch("jwt.decode", return_value={"prm": 1})
    result = is_premium_user("token")

    assert result is True

    mocker.patch("jwt.decode", return_value={"prm": 0})
    result = is_premium_user("token")

    assert result is False


def test_get_movie_by_id(mocker: MockFixture):
    movie_data = {
        "uuid": str(uuid4()),
        "title": "Title",
        "filename": "filename",
        "premium": True,
    }
    mocker.patch(
        "httpx.get",
        return_value=Response(status_code=200, content=json.dumps(movie_data)),
    )

    result = get_movie_by_id(movie_data["uuid"])

    assert result == Movie(**movie_data)

    mocker.patch(
        "httpx.get", return_value=Response(status_code=400, content=json.dumps({}))
    )

    with pytest.raises(HTTPException) as exc:
        get_movie_by_id(movie_data["uuid"])

    assert "From search_api private/film/<id>" in exc.value.detail
    assert 400 == exc.value.status_code
