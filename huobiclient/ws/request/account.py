from typing import Dict

from huobiclient.ws.request.abstract import AbstractWebsocketRequest


class WSAccountChangeDetails(AbstractWebsocketRequest):

    def __init__(self, mode: int):
        if mode not in (0, 1, 2):
            raise ValueError(f'Wrong mode value "{mode}"')
        self._mode = mode

    @property
    def topic(self) -> str:
        return f'accounts.update#{self._mode}'

    def subscribe(self) -> Dict:
        return {'action': 'sub', 'ch': self.topic}

    def ubsubscribe(self) -> Dict:
        return {'action': 'unsub', 'ch': self.topic}
