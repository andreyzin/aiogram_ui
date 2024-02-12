import functools
from typing import Any, Dict

from aiogram.dispatcher.event.bases import (
    MiddlewareEventType,
    MiddlewareType,
    NextMiddlewareType,
)
from aiogram.dispatcher.event.handler import CallbackType
from aiogram.types import TelegramObject


def wrap_middleware(
    middleware: MiddlewareType[MiddlewareEventType], handler: CallbackType
) -> NextMiddlewareType[MiddlewareEventType]:
    @functools.wraps(handler)
    def handler_wrapper(event: TelegramObject, kwargs: Dict[str, Any]) -> Any:
        return handler(event, **kwargs)

    _middleware = handler_wrapper
    for m in reversed([middleware]):
        _middleware = functools.partial(m, _middleware)

    return _middleware
