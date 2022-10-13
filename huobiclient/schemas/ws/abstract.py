import abc
from typing import Dict


class AbstractWebsocketRequest(abc.ABC):

    def topic(self) -> str:
        ...

    def subscribe(self) -> Dict:
        ...

    def unsubscribe(self) -> Dict:
        ...
