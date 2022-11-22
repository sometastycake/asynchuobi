import gzip
import json
from typing import Any, AsyncGenerator, Dict, Optional, Type

import aiohttp
from aiohttp import ClientWebSocketResponse

from huobiclient.auth import WebsocketAuth
from huobiclient.cfg import HUOBI_ACCESS_KEY, HUOBI_SECRET_KEY, HUOBI_WS_ASSET_AND_ORDER_URL, HUOBI_WS_MARKET_URL
from huobiclient.exceptions import WSHuobiError
from huobiclient.ws.subscribers.market import BaseMarketStream


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
        if self._socket is None:
            await self.connect()
        await self._socket.send_json(message)

    async def __aiter__(self) -> AsyncGenerator[Any, None]:
        if self._socket is None:
            raise RuntimeError('Web socket is not connected')
        async for message in self._socket:
            yield message.data  # type:ignore


class HuobiMarketWebsocket:

    def __init__(
        self,
        url: str = HUOBI_WS_MARKET_URL,
        connection: Type[WebsocketConnection] = WebsocketConnection,
        **connection_kwargs,
    ):
        self.connection = connection(url=url, **connection_kwargs)

    async def __aenter__(self):
        await self.connection.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()

    async def _pong(self, timestamp: int) -> None:
        await self.connection.send({'pong': timestamp})

    async def subscribe(self, stream: BaseMarketStream):
        for message in stream.subscribe():
            await self.connection.send(message)

    async def unsubscribe(self, stream: BaseMarketStream):
        for message in stream.unsubscribe():
            await self.connection.send(message)

    async def __aiter__(self) -> AsyncGenerator[Dict, None]:
        async for message in self.connection:
            data = json.loads(gzip.decompress(message))
            if 'ping' in data:
                await self._pong(data['ping'])
                continue
            yield data


class HuobiAccountOrderWebsocket:

    def __init__(
        self,
        url: str = HUOBI_WS_ASSET_AND_ORDER_URL,
        access_key: str = HUOBI_ACCESS_KEY,
        secret_key: str = HUOBI_SECRET_KEY,
        connection: Type[WebsocketConnection] = WebsocketConnection,
        **connection_kwargs,
    ):
        self._url = url
        self._access_key = access_key
        self._secret_key = secret_key
        self._connection = connection(url=url, **connection_kwargs)

    async def __aenter__(self) -> 'HuobiAccountOrderWebsocket':
        await self._connection.connect()
        await self.auth()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._connection.close()

    async def _pong(self, timestamp: int) -> None:
        message = {
            'action': 'pong',
            'data': {
                'ts': timestamp,
            },
        }
        await self._connection.send(message)

    async def auth(self) -> None:
        auth = WebsocketAuth(
            SecretKey=self._secret_key,
            accessKey=self._access_key,
        )
        message = {
            'action': 'req',
            'ch': 'auth',
            'params': auth.to_request(self._url, 'GET'),
        }
        await self._connection.send(message)
        recv = await self._connection.receive()
        code = recv['code']
        if code != 200:
            raise WSHuobiError(
                err_code=code,
                err_msg=recv['message'],
            )

    async def __aiter__(self) -> AsyncGenerator[Dict, None]:
        async for message in self._connection:
            data = json.loads(message)
            if data.get('action', '') == 'ping':
                await self._pong(data['data']['ts'])
                continue
            yield data
