"""Модуль содержит кастомные ошибки."""


class MissingSubscriptionError(Exception):
    """Вызывается в случае, когда фильм требует подписки."""


class MissingMovieFileError(Exception):
    """Вызывается в случае, когда файл фильма не найден."""
