import re
from abc import ABC, abstractmethod
from typing import Any, Optional
from urllib.parse import quote

from aiogram.types import WebAppInfo as WAI


class BAction(ABC):
    @abstractmethod
    def _make_ikm_kwargs(self) -> dict[str, Any]:
        raise NotImplementedError()


class OpenURL(BAction):
    def __init__(self, url: str):
        if url is None:
            raise AttributeError("URL is incorrect. Got None, expected str")

        if url is not None and not re.match(
            r"(https?://[\w\d:#@%?/;$()~_\+-=\\\.&]*)", url
        ):
            raise AttributeError("URL is incorrect")

        self._url = url

    @property
    def url(self):
        return self._url

    def _make_ikm_kwargs(self) -> dict[str, Any]:
        return {"url": self.url}


class OpenWebApp(BAction):
    def __init__(self, url: str):
        self.web_app = WAI(url=url)

    def _make_ikm_kwargs(self) -> dict[str, Any]:
        return {"web_app": self.web_app}


class ShareText(OpenURL):
    def __init__(self, url: str, text: Optional[str] = None):
        text = text or ""
        super().__init__(
            f"https://telegram.me/share/url?url={quote(url)}&text={quote(text)}"
        )
