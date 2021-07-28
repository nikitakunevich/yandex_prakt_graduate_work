from fastapi import HTTPException


class MissingSubscriptionError(Exception):
    pass


class MissingMovieFileError(Exception):
    pass


def raise_http_exception(exc, logger, status_code, detail):
    logger.exception(exc)
    raise HTTPException(
        status_code=400,
        detail="400: Expired token",
    ) from exc
