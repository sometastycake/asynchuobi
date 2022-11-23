import asyncio
import gzip
import json
from typing import AsyncGenerator, Dict, Type

from huobiclient.auth import WebsocketAuth
from huobiclient.cfg import HUOBI_ACCESS_KEY, HUOBI_SECRET_KEY, HUOBI_WS_ASSET_AND_ORDER_URL, HUOBI_WS_MARKET_URL
from huobiclient.exceptions import WSHuobiError
from huobiclient.ws.connection import WebsocketConnection
from huobiclient.ws.subscribers.market import BaseMarketStream


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
                asyncio.create_task(self._pong(data['ping']))
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
        if not self._access_key or not self._secret_key:
            raise ValueError('Access key or secret key can not be empty')

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
                asyncio.create_task(self._pong(data['data']['ts']))
                continue
            yield data
