from typing import Optional

from aiohttp import WSMessage

from asynchuobi.ws.ws_connection import WS_MESSAGE_TYPE, WebsocketConnectionAbstract


class WSConnectionStub(WebsocketConnectionAbstract):

    def __init__(self, *args, **kwargs):  # noqa
        self._closed = True
        self._position = 0
        self._sent_messages = []
        self._messages = kwargs.get('messages')

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
        else:
            await self.close()
        return message

    async def send(self, message: WS_MESSAGE_TYPE) -> None:
        self._sent_messages.append(message)
