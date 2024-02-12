from typing import Dict, Optional, Union

from aiogram.dispatcher.event.handler import CallbackType


class LayoutDP:
    def __init__(self):
        self._handlers: Dict[str, CallbackType] = {}

    def get(self, handler_name: str):
        if handler_name not in self._handlers:
            raise ValueError(f"Handler {handler_name} not found")
        return self._handlers[handler_name]

    def add(self, handler: CallbackType, name: Optional[str] = None):
        self._handlers[f"{name or handler.__name__}"] = handler

    def __call__(self, name: Optional[str] = None):
        def wrapper(handler: CallbackType):
            self.add(handler, name)
            return handler

        return wrapper

    def get_handler_name(self, handler: Union[str, CallbackType]) -> str:
        name = None
        if isinstance(handler, str) and handler in self._handlers:
            name = handler
        for i in self._handlers:
            if self._handlers[i] == handler:
                name = i
                break

        if name is not None:
            return name

        raise ValueError(f"Handler {handler} not found")
