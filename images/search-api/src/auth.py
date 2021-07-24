import logging
from enum import Enum

from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser, BaseUser,
)
import jwt

from registry import filter_premium
from config import config


class Roles(str, Enum):
    admin = "admin"
    child = "child"
    adult = "adult"
    premium = "premium"


def role_to_permissions(role: Roles):
    return _role_permissions[role]


class Permissions(str, Enum):
    filename_read = "movie.filename:read"
    premium_read = "premium:read"
    movie_read = "movie:read"
    movie_adult_read = "movie.adult:read"


_role_permissions = {
    Roles.premium: [
        Permissions.movie_read, Permissions.filename_read, Permissions.movie_adult_read, Permissions.premium_read
    ],
    Roles.admin: [Permissions.movie_read, Permissions.movie_adult_read, Permissions.filename_read],
    Roles.child: [Permissions.movie_read],
    Roles.adult: [Permissions.movie_read, Permissions.movie_adult_read]
}


class JWTAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        # Get JWT token from user's cookies

        if "Authorization" not in request.headers:
            logging.debug("no auth")
            return

        auth = request.headers["Authorization"]
        try:
            scheme, token = auth.split()
            if scheme.lower() != "bearer":
                logging.debug("not bearer auth")
                return
        except ValueError:
            logging.debug(f"Invalid authorization header: {auth}")
            raise AuthenticationError("Invalid authorization")

        # Returns UnauthenticatedUser if token does not exists in header
        if not token:
            logging.debug("no token")
            return

        # Checks the validity of the JWT token, if token is invalid returns UnauthenticatedUser object
        try:
            jwt_decoded = jwt.decode(
                token, config.JWT_PUBLIC_KEY, algorithms=[config.JWT_ALGORITHM]
            )
        except jwt.PyJWTError as err:
            logging.error(str(err))
            logging.exception("invalid token, user is unauthenticated")
            raise AuthenticationError("Invalid credentials")

        # In case if token is valid returns an object of the authorized user
        user_permissions = set()
        is_premium = jwt_decoded["prm"]
        if is_premium:
            filter_premium.set(False)
            user_permissions.add(Permissions.premium_read)
        logging.debug(
            f"token is valid, user: {jwt_decoded['sub']} roles: {jwt_decoded['roles']}, jwt: {jwt_decoded}"
        )
        for role in jwt_decoded["roles"].split(','):
            user_permissions.update(role_to_permissions(role))
        return AuthCredentials(list(user_permissions)), SimpleUser(jwt_decoded["sub"])
