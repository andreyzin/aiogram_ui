from typing import Any, Awaitable, Callable, Dict, Optional, Union, cast

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .context import LayoutContext
from .fsm_context import LayoutFSMContext
from .handler_dispatcher import LayoutDP
from .text_layout_data import TextLayoutData
from .tools import wrap_middleware


class LayoutMiddleware(BaseMiddleware):
    def __init__(
        self, layout_handler_dispatcher: Optional[LayoutDP] = None
    ):
        self.layout_dp = (
            layout_handler_dispatcher or LayoutDP()
        )

    async def __call__(
        self,
        handler: Callable[
            [Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]
        ],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        if data.get("layout_context") is None:
            data["layout_context"] = LayoutContext(
                event, layout_handler_dispatcher=self.layout_dp
            )

        layout_context = cast(LayoutContext, data["layout_context"])
        state = data.get("state")
        if isinstance(state, FSMContext) and state is not None:
            state = LayoutFSMContext(
                state.storage, state.key, self.layout_dp
            )
            data["state"] = state

        result = await handler(event, data)

        if isinstance(result, TextLayoutData):
            return await layout_context.set(result)

        if isinstance(result, Callable):
            wrapped_inner = wrap_middleware(
                self,
                HandlerObject(result).call,
            )
            result = await wrapped_inner(event, data)

        return result
