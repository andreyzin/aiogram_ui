from typing import Iterable, Optional, Sequence, Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .ikb import IKB


class IKM(InlineKeyboardMarkup):

    def __add__(self, other: Union[IKB, InlineKeyboardMarkup]) -> "IKM":
        """
        Method to add two IKM objects or an IKB object to the inline_keyboard list.

        Args:
            other: The object to be added to the inline_keyboard list.

        Returns:
            IKM: The resulting IKM object after the addition.

        Raises:
            ValueError: If the 'other' object is not an instance of IKB, IKM, or InlineKeyboardMarkup.
        """
        if isinstance(other, IKB):
            return IKM(inline_keyboard=self.inline_keyboard + [[other]])

        if isinstance(other, InlineKeyboardMarkup):
            return IKM(inline_keyboard=self.inline_keyboard + other.inline_keyboard)

        raise ValueError("Other should be IKB, IKM or InlineKeyboardMarkup")

    def without_line(self, line_n: int):
        """
        Remove a line from the inline keyboard and return a new IKM instance.

        Parameters:
            line_n (int): The number of the line to remove from the inline keyboard.

        Returns:
            IKM: A new IKM instance with the specified line removed.
        """
        if not isinstance(line_n, int):
            raise ValueError("Other should be number of line to remove")

        if len(self.inline_keyboard) < line_n:
            raise ValueError(
                f"Line number should be less then lines amount({len(self.inline_keyboard)})!"
            )

        return IKM(
            inline_keyboard=[
                self.inline_keyboard[i]
                for i in range(len(self.inline_keyboard))
                if i != line_n
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
    """
    Generates an InlineKeyboardMarkup with the provided buttons.

    The function takes a variable number of arguments, each of which can be an InlineKeyboardButton,
    a Sequence of InlineKeyboardButton, or an InlineKeyboardMarkup.
    The 'vertical' parameter is a boolean that determines the layout of the buttons.
    Returns an InlineKeyboardMarkup.
    """
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
