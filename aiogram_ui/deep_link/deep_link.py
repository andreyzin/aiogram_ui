from decimal import Decimal
from enum import Enum
from fractions import Fraction
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Optional, Type, TypeVar, Union
from uuid import UUID

from aiogram import Bot
from aiogram.filters.command import Command, CommandException
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload, encode_payload
from aiogram.utils.magic_filter import MagicFilter
from pydantic import BaseModel

T = TypeVar("T", bound="DeepLink")

MAX_PAYLOAD_LENGTH = 64


class DeepLink(BaseModel):
    """
    Base class for deep link wrapper

    This class should be used as super-class of user-defined callbacks.

    The class-keyword :code:`prefix` is required to define prefix
    and also the argument :code:`sep` can be passed to define separator (default is :code:`:`)
    and :code:`is_plain` can be passed to define if is plain deep link(without base64url encoding)
    """

    if TYPE_CHECKING:
        __separator__: ClassVar[str]
        """Data separator (default is :code:`_`)"""
        __prefix__: ClassVar[str]
        """Callback prefix"""
        __is_plain__: ClassVar[bool]
        """If is plain deep link(without base64url encoding)"""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        cls.__separator__ = kwargs.pop("sep", "_")
        cls.__prefix__ = kwargs.pop("prefix", "")
        cls.__is_plain__ = kwargs.pop("is_plain", False)

        if cls.__separator__ in cls.__prefix__:
            raise ValueError(
                f"Separator symbol {cls.__separator__!r} can not be used "
                f"inside prefix {cls.__prefix__!r}"
            )
        super().__init_subclass__(**kwargs)

    def _encode_value(self, key: str, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, Enum):
            return str(value.value)
        if isinstance(value, UUID):
            return value.hex
        if isinstance(value, bool):
            return str(int(value))
        if isinstance(value, (int, str, float, Decimal, Fraction)):
            return str(value)
        raise ValueError(
            f"Attribute {key}={value!r} of type {type(value).__name__!r}"
            f" can not be packed to callback data"
        )

    def pack(self) -> str:
        """
        Generate callback data string

        :return: valid callback data for Telegram Bot API
        """
        result = []
        if self.__prefix__:
            result.append(self.__prefix__)

        for key, value in self.model_dump(mode="json").items():
            encoded = self._encode_value(key, value)
            if self.__separator__ in encoded:
                raise ValueError(
                    f"Separator symbol {self.__separator__!r} can not be used "
                    f"in value {key}={encoded!r}"
                )
            result.append(encoded)

        callback_data = self.__separator__.join(result)
        return callback_data

    @classmethod
    def unpack(cls: Type[T], value: str) -> T:
        """
        Parse payload data string

        :param value: payload from Telegram
        :return: instance of DeepLink
        """
        if not isinstance(value, str):
            raise TypeError("value should be str")
        parts = value.split(cls.__separator__)
        names = cls.model_fields.keys()
        prefix = ""
        if cls.__prefix__ and cls.__prefix__ == parts[0]:
            prefix = parts[0]
            parts = parts[1:]

        if len(parts) != len(names):
            raise TypeError(
                f"Callback data {cls.__name__!r} takes {len(names)} arguments "
                f"but {len(parts)} were given"
            )
        if prefix != cls.__prefix__:
            raise ValueError(f"Bad prefix ({prefix!r} != {cls.__prefix__!r})")
        payload = {}
        for k, v in zip(names, parts):
            if field := cls.model_fields.get(k):
                if v == "" and not field.is_required():
                    v = None
            payload[k] = v
        return cls(**payload)

    def encode(self):
        if self.__is_plain__:
            return self.pack()
        return encode_payload(self.pack())

    def get_link(self, bot_username: str):
        return f"https://t.me/{bot_username}?start={self.encode()}"

    @classmethod
    def decode(cls, payload: str):
        if cls.__is_plain__:
            return cls.unpack(payload)
        return cls.unpack(decode_payload(payload))

    @classmethod
    def filter(cls, rule: Optional[MagicFilter] = None) -> "DeepLinkFilter":
        """
        Generates a filter for deep_link with rule

        :param rule: magic rule
        :return: instance of filter
        """
        return DeepLinkFilter(deep_link=cls, rule=rule)


class DeepLinkFilter(Command):
    """
    This filter helps to handle deeplinks.

    Should not be used directly, you should create the instance of this filter
    via deep link instance
    """

    def __init__(
        self,
        deep_link: Type[DeepLink],
        rule: Optional[MagicFilter] = None,
    ):
        self.deep_link = deep_link
        self.rule = rule
        super().__init__("start")

    async def __call__(self, message: Message, bot: Bot) -> Union[bool, Dict[str, Any]]:
        if not isinstance(message, Message):
            return False

        text = message.text or message.caption
        if not text:
            return False

        try:
            command = await self.parse_command(text=text, bot=bot)
            assert command.args
            deep_link = self.deep_link.decode(command.args)
        except CommandException:
            return False
        except (TypeError, ValueError):
            return False

        if self.rule is None or self.rule.resolve(deep_link):
            return {"deep_link": deep_link}
        return False
