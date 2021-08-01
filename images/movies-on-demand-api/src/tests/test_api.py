from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockFixture
from requests import Session

from models import Movie

signed_url = "signed_url"

create_private_link_success = (
    True,
    {
        "uuid": str(uuid4()),
        "title": "Title",
        "filename": "filename",
        "premium": True,
    },
    signed_url,
    200,
    {"url": signed_url},
)


create_private_link_trial = (
    False,
    {
        "uuid": str(uuid4()),
        "title": "Title",
        "filename": "filename",
        "premium": True,
    },
    signed_url,
    403,
    {"detail": "Missing subscription"},
)


create_private_link_missing_file = (
    False,
    {"uuid": str(uuid4()), "title": "Title", "filename": None, "premium": True},
    signed_url,
    404,
    {"detail": "No existing video file for movie"},
)


@pytest.mark.parametrize(
    "premium_user,movie_data,signed_url,expected_status,expected_resp",
    [
        create_private_link_success,
        create_private_link_trial,
        create_private_link_missing_file,
    ],
)
def test_create_private_link(
    premium_user: bool,
    movie_data: dict,
    signed_url: str,
    expected_status: int,
    expected_resp: dict,
    mocker: MockFixture,
    app: FastAPI,
):
    client: Session = TestClient(app)
    headers = {"Authorization": "Bearer token"}

    movie = Movie(**movie_data)

    mocker.patch("api.v1.is_premium_user", return_value=premium_user)
    mocker.patch("api.v1.get_movie_by_id", return_value=movie)
    mocker.patch("api.v1.get_signed_url", return_value=signed_url)

    movie_uid = str(uuid4())
    response = client.post(
        app.url_path_for("create_private_link"), json={"id": movie_uid}, headers=headers
    )

    assert response.status_code == expected_status
    assert response.json() == expected_resp
