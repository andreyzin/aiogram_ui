from typing import Iterable, Optional, Sequence, Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .ikb import IKB


class IKM(InlineKeyboardMarkup):

    def __add__(self, other) -> "IKM":
        if isinstance(other, IKB):
            return IKM(inline_keyboard=self.inline_keyboard + [[other]])

        if isinstance(other, InlineKeyboardMarkup):
            return IKM(inline_keyboard=self.inline_keyboard + other.inline_keyboard)

        raise ValueError("Other should be IKB, IKM or InlineKeyboardMarkup")

    def without_line(self, other: int):
        if not isinstance(other, int):
            raise ValueError("Other should be number of line to remove")

        if len(self.inline_keyboard) < other:
            raise ValueError(
                f"Line number should be less then lines amount({len(self.inline_keyboard)})!"
            )

        return IKM(
            inline_keyboard=[
                self.inline_keyboard[i]
                for i in range(len(self.inline_keyboard))
                if i != other
            ]
        )


def KB(
    *args: Union[
        InlineKeyboardButton,
        None,
        Sequence[Optional[InlineKeyboardButton]],
        InlineKeyboardMarkup,
    ],
    vertical=True,
):
    inline_keyboard = []
    i = 0
    while i < len(args):
        current = args[i]
        # FOR LIST OF BUTTONS
        if isinstance(current, Sequence):
            group = []
            for item in current:
                if isinstance(item, InlineKeyboardButton):
                    group.append(item)

            if group:
                inline_keyboard.append(group)

        # FOR InlineKeyboardMarkup INSTANCE
        if isinstance(current, InlineKeyboardMarkup):
            inline_keyboard += current.inline_keyboard

        # FOR SEQUENCE OF BUTTONS
        group = []
        while i < len(args) and (
            isinstance(args[i], InlineKeyboardButton) or args[i] is None
        ):
            if args[i]:
                group.append(args[i])
            i += 1

        if group:
            inline_keyboard += [[btn] for btn in group] if vertical else [group]
            i -= 1

        i += 1

    return IKM(inline_keyboard=inline_keyboard)
