import abc
from typing import Dict, Optional, Type

import aiohttp
from aiohttp import ClientWebSocketResponse, WSMessage

WS_MESSAGE_TYPE = Dict


class WebsocketConnectionAbstract(abc.ABC):

    @abc.abstractmethod
    def __init__(self, *args, **kwargs): ...

    @property
    @abc.abstractmethod
    def closed(self) -> bool: ...

    @abc.abstractmethod
    async def close(self) -> None: ...

    @abc.abstractmethod
    async def connect(self, **kwargs) -> None: ...

    @abc.abstractmethod
    async def receive(self, timeout: Optional[float] = None) -> WSMessage: ...

    @abc.abstractmethod
    async def send(self, message: WS_MESSAGE_TYPE) -> None: ...


class WebsocketConnection(WebsocketConnectionAbstract):

    def __init__(
        self,
        url: str,
        session: Type[aiohttp.ClientSession] = aiohttp.ClientSession,
        **session_kwargs,
    ):
        self._url = url
        if session_kwargs.get('connector') is None:
            session_kwargs['connector'] = aiohttp.TCPConnector(ssl=False)
        self._session = session(**session_kwargs)
        self._socket: Optional[ClientWebSocketResponse] = None

    def __del__(self):
        if self._session and self._session.connector:
            if not self._session.connector.closed:
                self._session.connector.close()

    @property
    def closed(self) -> bool:
        if self._socket is None:
            return True
        return self._socket.closed and self._session.closed

    async def close(self) -> None:
        if self._socket is not None:
            await self._socket.close()
        await self._session.close()

    async def connect(self, **kwargs) -> None:
        self._socket = await self._session.ws_connect(url=self._url, **kwargs)

    async def receive(self, timeout: Optional[float] = None) -> WSMessage:
        if self._socket is None:
            raise RuntimeError('Web socket is not connected')
        return await self._socket.receive(timeout)

    async def send(self, message: WS_MESSAGE_TYPE) -> None:
        if self._socket is None:
            await self.connect()
        await self._socket.send_json(message)  # type:ignore[union-attr]
