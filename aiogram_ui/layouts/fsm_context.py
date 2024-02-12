from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union

from aiogram.dispatcher.event.handler import CallbackType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from cachetools import TTLCache

if TYPE_CHECKING:
    from .handler_dispatcher import LayoutDP


class LayoutFSMContext(FSMContext):
    _prefix: str = "__lt_ctx:"
    _cache: TTLCache[StorageKey, Dict] = TTLCache(maxsize=128, ttl=60 * 60)

    def __init__(
        self,
        storage: BaseStorage,
        key: StorageKey,
        layout_handler_dispatcher: "LayoutDP",
    ) -> None:
        self.storage = storage
        self.key = key
        self._layout_handler_dispatcher = layout_handler_dispatcher

    def _separate_data(
        self, data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        state_data = {}
        layout_data = {}
        for i, v in data.items():
            if i.startswith(self._prefix):
                layout_data[i] = v
            else:
                state_data[i] = v

        return state_data, layout_data

    def _add_prefix(self, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        return {self._prefix + i: v for i, v in layout_data.items()}

    def _remove_prefix(self, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        return {i.removeprefix(self._prefix): v for i, v in layout_data.items()}

    async def _get_data(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if self.key in self.__class__._cache:
            data = self.__class__._cache[self.key]
        else:
            data = await self.storage.get_data(key=self.key)
            self.__class__._cache[self.key] = data

        return self._separate_data(data)

    async def _set_data(self, data: Dict[str, Any]) -> None:
        self.__class__._cache[self.key] = data
        await self.storage.set_data(key=self.key, data=data)

    async def _update_data(
        self, data: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if data:
            kwargs.update(data)

        new_data = await self.storage.update_data(
            key=self.key,
            data=kwargs,
        )
        self.__class__._cache[self.key] = new_data
        return self._separate_data(new_data)

    async def set_data(self, data: Dict[str, Any]) -> None:
        _, layout_data = await self._get_data()
        await self._set_data(data=data | layout_data)

    async def get_data(self) -> Dict[str, Any]:
        state_data, _ = await self._get_data()
        return state_data

    async def update_data(
        self, data: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        if data:
            kwargs.update(data)

        new_state_data, _ = await self._update_data(kwargs)
        return new_state_data

    async def clear(self) -> None:
        await self.set_state(state=None)
        _, layout_data = await self._get_data()
        await self._set_data(data=layout_data)

    async def drop(self) -> None:
        await self.set_state(state=None)
        await self._set_data(data={})

    async def get_layout_data(self) -> Dict[str, Any]:
        _, layout_data = await self._get_data()
        return self._remove_prefix(layout_data)

    async def update_layout_data(
        self, layout_data: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        if layout_data:
            kwargs.update(layout_data)

        _, new_layout_data = await self._update_data(self._add_prefix(kwargs))
        return self._remove_prefix(new_layout_data)

    async def set_layout_data(self, layout_data: Dict[str, Any]) -> None:
        state_data, _ = await self._get_data()
        layout_data = self._add_prefix(layout_data)
        await self._set_data(data=state_data | layout_data)

    async def set_next_callback(self, callback: Union[CallbackType, str]) -> None:
        name = self._layout_handler_dispatcher.get_handler_name(callback)
        await self.update_layout_data(next_callback=name)

    async def pop_next_callback(self) -> CallbackType:
        data = await self.get_layout_data()
        next_callback_name = data.pop("next_callback", None)
        if next_callback_name:
            next_callback = self._layout_handler_dispatcher.get(next_callback_name)
            await self.set_layout_data(data)
            return next_callback

        raise ValueError("No next callback found")
