import asyncio
import gzip
import json
from typing import Any, AsyncGenerator, Callable, Dict, Type, Union

from huobiclient.auth import WebsocketAuth
from huobiclient.exceptions import WSHuobiError
from huobiclient.urls import HUOBI_WS_ASSET_AND_ORDER_URL, HUOBI_WS_MARKET_URL
from huobiclient.ws.connection import WebsocketConnection
from huobiclient.ws.enums import TradeDetailMode
from huobiclient.ws.subscribers.market import BaseMarketStream

LOADS_TYPE = Callable[[Union[str, bytes]], Any]


class HuobiMarketWebsocket:

    def __init__(
        self,
        url: str = HUOBI_WS_MARKET_URL,
        loads: LOADS_TYPE = json.loads,
        decompress: Callable[[bytes], bytes] = gzip.decompress,
        connection: Type[WebsocketConnection] = WebsocketConnection,
        **connection_kwargs,
    ):
        self._loads = loads
        self._decompress = decompress
        self._connection = connection(url=url, **connection_kwargs)

    async def __aenter__(self):
        await self._connection.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._connection.close()

    async def _pong(self, timestamp: int) -> None:
        await self._connection.send({'pong': timestamp})

    async def subscribe(self, stream: BaseMarketStream):
        for message in stream.subscribe():
            await self._connection.send(message)

    async def unsubscribe(self, stream: BaseMarketStream):
        for message in stream.unsubscribe():
            await self._connection.send(message)

    async def __aiter__(self) -> AsyncGenerator[Dict, None]:
        async for message in self._connection:
            data = self._loads(self._decompress(message))
            if 'ping' in data:
                asyncio.create_task(self._pong(data['ping']))
                continue
            yield data


class HuobiAccountOrderWebsocket:

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        url: str = HUOBI_WS_ASSET_AND_ORDER_URL,
        loads: LOADS_TYPE = json.loads,
        connection: Type[WebsocketConnection] = WebsocketConnection,
        **connection_kwargs,
    ):
        self._url = url
        self._loads = loads
        self._access_key = access_key
        self._secret_key = secret_key
        self._connection = connection(url=url, **connection_kwargs)
        if not self._access_key or not self._secret_key:
            raise ValueError('Access key or secret key can not be empty')

    async def __aenter__(self) -> 'HuobiAccountOrderWebsocket':
        await self._connection.connect()
        await self.auth()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa: U100
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

    async def subscribe_order_updates(self, symbol: str) -> None:
        if not isinstance(symbol, str):
            raise TypeError('Symbol is not str')
        await self._connection.send({
            'action': 'sub',
            'ch': f'orders#{symbol}',
        })

    async def subscribe_trade_detail(
            self,
            symbol: str,
            mode: TradeDetailMode = TradeDetailMode.only_trade_event,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError('Symbol is not str')
        await self._connection.send({
            'action': 'sub',
            'ch': f'trade.clearing#{symbol}#{mode.value}',
        })

    async def subscribe_account_change(self, mode: int = 0) -> None:
        if mode not in (0, 1, 2):
            raise ValueError('Wrong mode value')
        await self._connection.send({
            'action': 'sub',
            'ch': f'accounts.update#{mode}',
        })

    async def __aiter__(self) -> AsyncGenerator[Dict, None]:
        async for message in self._connection:
            data = self._loads(message)
            if data.get('action', '') == 'ping':
                asyncio.create_task(self._pong(data['data']['ts']))
                continue
            yield data
