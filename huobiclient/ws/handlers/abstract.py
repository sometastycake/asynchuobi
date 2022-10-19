import abc
from typing import Any, Dict, Optional

from aiohttp import WSMessage


class AbstractWebsocketMessageHandler(abc.ABC):

    @abc.abstractmethod
    def decode(self, message: WSMessage) -> Dict:  # noqa:U100
        ...

    @abc.abstractmethod
    def check_error(self, message: Dict) -> None:  # noqa:U100
        ...

    @abc.abstractmethod
    def is_ping(self, message: WSMessage) -> Optional[int]:  # noqa:U100
        ...

    @abc.abstractmethod
    def __call__(self, message: WSMessage) -> Any:  # noqa:U100
        ...
