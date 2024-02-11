from datetime import timezone
from datetime import datetime, timedelta, tzinfo
from typing import Any
from aiogram.filters.callback_data import MAX_CALLBACK_LENGTH
from aiogram.filters.callback_data import CallbackData as AiogramCallbackData
from pydantic import ValidationInfo, field_serializer, field_validator, root_validator


class CallbackData(AiogramCallbackData, prefix=""):
    """
    Base class for callback data wrapper

    This class should be used as super-class of user-defined callbacks.

    The class-keyword :code:`prefix` is required to define prefix
    and also the argument :code:`sep` can be passed to define separator (default is :code:`:`).
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def pack(self) -> str:
        """
        Generate callback data string

        :return: valid callback data for Telegram Bot API
        """
        result = [self.__prefix__]
        for key, value in self.model_dump().items():
            encoded = self._encode_value(key, value)
            if self.__separator__ in encoded:
                raise ValueError(
                    f"Separator symbol {self.__separator__!r} can not be used "
                    f"in value {key}={encoded!r}"
                )
            result.append(encoded)
        callback_data = self.__separator__.join(result)
        if len(callback_data.encode()) > MAX_CALLBACK_LENGTH:
            raise ValueError(
                f"Resulted callback data is too long! "
                f"len({callback_data!r}.encode()) > {MAX_CALLBACK_LENGTH}"
            )
        return callback_data

    def _encode_value(self, key: str, value: Any) -> str:
        if isinstance(value, datetime):
            return str(int(datetime.timestamp(value)))
        return super()._encode_value(key, value)

    @field_validator("*", mode="after")
    @classmethod
    def _validate_datetime(cls, v: Any, f: ValidationInfo):
        if isinstance(v, datetime):
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v.utcoffset() is None:
                v = v.replace(tzinfo=timezone.utc)
        return v
