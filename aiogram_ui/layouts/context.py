from typing import TYPE_CHECKING, Optional, Union

from aiogram.dispatcher.event.handler import CallbackType
from aiogram.types import CallbackQuery, Message

from .text_layout_data import TextLayoutData

if TYPE_CHECKING:
    from .handler_dispatcher import LayoutDP


class LayoutContext:
    def __init__(
        self,
        original_event: Union[Message, CallbackQuery],
        layout_handler_dispatcher: "LayoutDP",
    ):
        self.original_event = original_event
        self._layout_handler_dispatcher = layout_handler_dispatcher
        self._events = [original_event]

    @property
    def is_original(self):
        return len(self._events) == 1

    async def set(self, layout: TextLayoutData):
        event = await layout.set(self._events[-1])
        if isinstance(event, Message):
            self._events.append(event)
        return event

    async def send(self, layout: TextLayoutData):
        event = await layout.send(self.original_event)
        self._events.append(event)
        return event

    async def send_to(self, layout: TextLayoutData, chat_id: Union[int, str]):
        assert self.original_event.bot, "event.bot must be set before using this layout"
        event = await layout.send_to(chat_id, self.original_event.bot)
        self._events.append(event)
        return event

    def run(
        self, handler: Union[str, CallbackType], callback: Optional[CallbackType] = None
    ) -> CallbackType:
        if callback:
            ...
        if isinstance(handler, str):
            handler_ = self._layout_handler_dispatcher.get(handler)
            if handler_ is None:
                raise ValueError(f"Handler {handler} not found")
            handler = handler_

        return handler
