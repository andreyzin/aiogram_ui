from typing import Optional, Union

from aiogram import Bot
from aiogram.methods import EditMessageText, SendMessage
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from pydantic import BaseModel, ConfigDict


class TextLayoutData(BaseModel):
    model_config = ConfigDict(extra="allow")

    text: str
    reply_markup: Optional[InlineKeyboardMarkup] = None

    def set(
        self, event: Union[Message, CallbackQuery], **kwargs
    ) -> Union[SendMessage, EditMessageText]:
        assert event.bot is not None, "event.bot must be set before using this layout"
        kw = self.model_dump() | kwargs
        message = event if isinstance(event, Message) else event.message
        if (
            isinstance(message, Message)
            and message.from_user
            and message.from_user.id == event.bot.id
        ):
            kw = kw | {
                "chat_id": message.chat.id,
                "message_id": message.message_id,
            }
            return EditMessageText(**kw).as_(event.bot)

        return self.send(event, **kw)

    def send(self, event: Union[Message, CallbackQuery], **kwargs) -> SendMessage:
        assert event.bot is not None, "event.bot must be set before using this layout"
        kw = self.model_dump() | kwargs
        chat_id = None
        if isinstance(event, Message):
            chat_id = event.chat.id
        elif (
            isinstance(event, CallbackQuery) and event.message and event.message.chat.id
        ):
            chat_id = event.message.chat.id
        assert chat_id is not None, "chat_id cant be fetched from event"
        return self.send_to(chat_id, event.bot, **kw)

    def send_to(self, chat_id: Union[int, str], bot: Bot, **kwargs):
        kw = self.model_dump() | kwargs | {"chat_id": chat_id}
        return SendMessage(**kw).as_(bot)
