from typing import Optional, Union

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from .b_action import BAction


class IKB(InlineKeyboardButton):
    def with_text(self, text: str):
        return IKB(text=text, callback_data=self.callback_data)


def B(
    text: str, action: Union[str, CallbackData, BAction], show: bool = True
) -> Optional[IKB]:
    """
    A function that takes in a text string, an action (which can be a string, CallbackData, or BAction), 
    and a boolean flag show. 
    It returns an IKB object if show is True, otherwise it returns None.
    """
    if not show:
        return None

    if isinstance(action, BAction):
        return IKB(text=text, **action._make_ikm_kwargs())

    if isinstance(action, CallbackData):
        action = action.pack()

    return IKB(text=text, callback_data=action)
