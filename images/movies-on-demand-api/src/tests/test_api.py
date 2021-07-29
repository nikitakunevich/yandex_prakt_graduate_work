from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockFixture
from requests import Session

from models import Movie


def test_create_private_link_success(mocker: MockFixture, app: FastAPI):
    client: Session = TestClient(app)
    headers = {"Authorization": "Bearer token"}

    movie = Movie(
        **{
            "uuid": str(uuid4()),
            "title": "Title",
            "filename": "filename",
            "premium": True,
        }
    )

    signed_url = "signed_url"
    mocker.patch("api.v1.is_premium_user", return_value=True)
    mocker.patch("api.v1.get_movie_by_id", return_value=movie)
    mocker.patch("api.v1.get_signed_url", return_value=signed_url)

    movie_uid = str(uuid4())
    response = client.post(
        app.url_path_for("create_private_link"), json={"id": movie_uid}, headers=headers
    )

    assert response.status_code == 200
    assert response.json() == {"url": signed_url}


def test_create_private_link_trial(mocker: MockFixture, app: FastAPI):
    client: Session = TestClient(app)
    headers = {"Authorization": "Bearer token"}

    movie = Movie(
        **{
            "uuid": str(uuid4()),
            "title": "Title",
            "filename": "filename",
            "premium": True,
        }
    )

    mocker.patch("api.v1.is_premium_user", return_value=False)
    mocker.patch("api.v1.get_movie_by_id", return_value=movie)

    movie_uid = str(uuid4())
    response = client.post(
        app.url_path_for("create_private_link"), json={"id": movie_uid}, headers=headers
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Missing subscription"}


def test_create_private_link_missing_file(mocker: MockFixture, app: FastAPI):
    client: Session = TestClient(app)
    headers = {"Authorization": "Bearer token"}

    movie = Movie(
        **{"uuid": str(uuid4()), "title": "Title", "filename": None, "premium": True}
    )

    mocker.patch("api.v1.is_premium_user", return_value=False)
    mocker.patch("api.v1.get_movie_by_id", return_value=movie)

    movie_uid = str(uuid4())
    response = client.post(
        app.url_path_for("create_private_link"), json={"id": movie_uid}, headers=headers
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No existing video file for movie"}
