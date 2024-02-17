from aiogram.types import CallbackQuery


class FilterableStr(str):
    """
    A class representing a string that can be used as aiogram filter

    Is good to use with CallbackData class

    :code:`@dp.callback_query(FilterableStr("test"))`

    is the same as
    :code:`@dp.callback_query(F.data == "test")`
    """

    def filter(self, callback_query: CallbackQuery):
        return callback_query.data == self

    __call__ = filter
