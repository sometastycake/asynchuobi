import gzip
import json
from typing import Optional

from aiohttp import WSMessage, WSMsgType

from asynchuobi.ws.ws_connection import WS_MESSAGE_TYPE, WebsocketConnectionAbstract


class HuobiMarketWebsocketConnectionStub(WebsocketConnectionAbstract):

    def __init__(self, *arg, **kwargs):
        self._closed = True
        self._position = 0
        self._sent_messages = []
        self._messages = [
            WSMessage(
                type=WSMsgType.BINARY,
                data=gzip.compress(
                    data=json.dumps({
                        'ping': 1,
                    }).encode(),
                ),
                extra=None,
            ),
            WSMessage(
                type=WSMsgType.BINARY,
                data=gzip.compress(
                    data=json.dumps({
                        'id': 'id',
                        'status': 'ok',
                        'subbed': 'market.btcusdt.kline.1min',
                        'ts': 1,
                    }).encode(),
                ),
                extra=None,
            ),
            WSMessage(
                type=WSMsgType.BINARY,
                data=gzip.compress(
                    data=json.dumps({
                        'ping': 2,
                    }).encode(),
                ),
                extra=None,
            ),
            WSMessage(
                type=WSMsgType.BINARY,
                data=gzip.compress(
                    data=json.dumps({
                        'id': 'id',
                        'status': 'error',
                        'err-code': 'code',
                        'err-msg': 'msg',
                        'ts': 1,
                    }).encode(),
                ),
                extra=None,
            ),
            WSMessage(
                type=WSMsgType.CLOSED,
                extra=None,
                data=None,
            ),
        ]

    @property
    def closed(self) -> bool:
        return self._closed

    async def close(self) -> None:
        self._closed = True

    async def connect(self, **kwargs) -> None:
        self._closed = False

    async def receive(self, timeout: Optional[float] = None) -> WSMessage:
        message = self._messages[self._position]
        if self._position < len(self._messages) - 1:
            self._position += 1
        return message

    async def send(self, message: WS_MESSAGE_TYPE) -> None:
        self._sent_messages.append(message)
