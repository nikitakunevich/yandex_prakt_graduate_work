"""Модуль содержит кастомные ошибки."""
from fastapi import HTTPException


class MissingSubscriptionError(HTTPException):
    """Вызывается в случае, когда фильм требует подписки."""

    def __init__(self):
        self.status_code = 403
        self.detail = "Missing subscription"


class MissingMovieFileError(HTTPException):
    """Вызывается в случае, когда файл фильма не найден."""

    def __init__(self):
        self.status_code = 404
        self.detail = "No existing video file for movie"
