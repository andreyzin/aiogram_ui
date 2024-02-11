from aiogram.types import CallbackQuery


class FilterableStr(str):
    def filter(self, callback_query: CallbackQuery):
        return callback_query.data == self

    __call__ = filter
