import gzip
import json
from typing import Any, Callable, Dict, Optional, Union

from aiohttp import WSMessage

from huobiclient.exceptions import WSHuobiError
from huobiclient.ws.handlers.abstract import AbstractWebsocketMessageHandler

JSONDecoder = Callable[[Union[str, bytes]], Any]


class MarketWebsocketMessageHandler(AbstractWebsocketMessageHandler):

    def __init__(self, json_decoder: JSONDecoder = json.loads):
        self._json_decoder = json_decoder

    def decode(self, message: WSMessage) -> Dict:
        return self._json_decoder(gzip.decompress(message.data))

    def check_error(self, message: Dict) -> None:
        if message.get('status', '') == 'error':
            raise WSHuobiError(
                err_code=message['err-code'],
                err_msg=message['err-msg'],
            )

    def is_ping(self, message: WSMessage) -> Optional[int]:
        return self.decode(message).get('ping')

    def __call__(self, message: WSMessage) -> Dict:
        decoded = self.decode(message)
        self.check_error(decoded)
        return decoded


class AccountOrderWebsocketMessageHandler(AbstractWebsocketMessageHandler):

    def __init__(self, json_decoder: JSONDecoder = json.loads):
        self._json_decoder = json_decoder

    def decode(self, message: WSMessage) -> Dict:
        return self._json_decoder(message.data)

    def check_error(self, message: Dict) -> None:
        if message.get('code', -1) != 200:
            raise WSHuobiError(
                err_code=message['code'],
                err_msg=message['message'],
            )

    def is_ping(self, message: WSMessage) -> Optional[int]:
        decoded = self.decode(message)
        action: Optional[str] = decoded.get('action', '')
        if action == 'ping':
            return decoded['data']['ts']
        return None

    def __call__(self, message: WSMessage) -> Dict:
        decoded = self.decode(message)
        self.check_error(decoded)
        return decoded
