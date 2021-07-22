import asyncio
import functools
import inspect
import logging
import typing

from starlette.authentication import has_required_scope, BaseUser, AuthCredentials
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.websockets import WebSocket

from auth import Permissions

logger = logging.getLogger(__name__)


def require_roles(
    scopes: typing.Union[str, typing.Sequence[str]],
    status_code: int = 403,
    redirect: str = None,
) -> typing.Callable:
    scopes_list = [scopes] if isinstance(scopes, str) else list(scopes)

    def decorator(func: typing.Callable) -> typing.Callable:
        type = None
        sig = inspect.signature(func)
        for idx, parameter in enumerate(sig.parameters.values()):
            if parameter.name == "request" or parameter.name == "websocket":
                type = parameter.name
                break
        else:
            raise Exception(
                f'No "request" or "websocket" argument on function "{func}"'
            )

        if type == "websocket":
            # Handle websocket functions. (Always async)
            @functools.wraps(func)
            async def websocket_wrapper(
                *args: typing.Any, **kwargs: typing.Any
            ) -> None:
                websocket = kwargs["websocket"]
                assert isinstance(websocket, WebSocket)

                if not has_required_scope(websocket, scopes_list):
                    await websocket.close()
                else:
                    await func(*args, **kwargs)

            return websocket_wrapper

        elif asyncio.iscoroutinefunction(func):
            # Handle async request/response functions.
            @functools.wraps(func)
            async def async_wrapper(
                *args: typing.Any, **kwargs: typing.Any
            ) -> Response:
                request = kwargs["request"]
                assert isinstance(request, Request)

                if not has_required_scope(request, scopes_list):
                    if redirect is not None:
                        return RedirectResponse(
                            url=request.url_for(redirect), status_code=303
                        )
                    raise HTTPException(status_code=status_code)
                return await func(*args, **kwargs)

            return async_wrapper

        else:
            # Handle sync request/response functions.
            @functools.wraps(func)
            def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
                request = kwargs["request"]
                assert isinstance(request, Request)

                if not has_required_scope(request, scopes_list):
                    if redirect is not None:
                        return RedirectResponse(
                            url=request.url_for(redirect), status_code=303
                        )
                    raise HTTPException(status_code=status_code)
                return func(*args, **kwargs)

            return sync_wrapper

    return decorator


def can_read_premium(auth: AuthCredentials) -> bool:
    logger.info(f"can_read_premium, auth: {auth}")

    return Permissions.premium_read in auth.scopes
