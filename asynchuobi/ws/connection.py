from typing import Any, AsyncGenerator, Dict, Optional, Type

import aiohttp
from aiohttp import ClientWebSocketResponse


class WebsocketConnection:

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

    async def close(self) -> None:
        await self._session.close()
        if self._socket is not None:
            await self._socket.close()
            self._socket = None

    async def connect(self, **kwargs) -> None:
        self._socket = await self._session.ws_connect(url=self._url, **kwargs)

    async def receive(self) -> Dict:
        if self._socket is None:
            raise RuntimeError('Web socket is not connected')
        return await self._socket.receive_json()

    async def send(self, message: Dict) -> None:
        if self._socket is None or self._socket.closed:
            await self.connect()
        await self._socket.send_json(message)

    async def __aiter__(self) -> AsyncGenerator[Any, None]:
        if self._socket is None:
            raise RuntimeError('Web socket is not connected')
        async for message in self._socket:
            yield message.data  # type:ignore
