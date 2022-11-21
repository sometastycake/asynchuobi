import gzip
import json
from typing import AsyncGenerator, Dict, Optional

from aiohttp import ClientSession, ClientWebSocketResponse, TCPConnector

from huobiclient.auth import WebsocketAuth
from huobiclient.cfg import HUOBI_ACCESS_KEY, HUOBI_SECRET_KEY, HUOBI_WS_ASSET_AND_ORDER_URL, HUOBI_WS_MARKET_URL
from huobiclient.exceptions import WSHuobiError
from huobiclient.ws.subscribers.market import BaseMarketStream


class HuobiWebsocket:

    def __init__(self, ws_url: str):
        self._ws_url = ws_url
        self._session: Optional[ClientSession] = None
        self._socket: Optional[ClientWebSocketResponse] = None

    async def __aenter__(self) -> 'HuobiWebsocket':
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @property
    def socket(self) -> ClientWebSocketResponse:
        if self._socket is None:
            raise RuntimeError('WS is not initialized')
        return self._socket

    async def close(self) -> None:
        if self._socket is not None and not self._socket.closed:
            await self._socket.close()
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def connect(self) -> None:
        self._session = ClientSession(
            connector=TCPConnector(ssl=False),
        )
        self._socket = await self._session.ws_connect(
            autoping=False,
            url=self._ws_url,
        )


class HuobiMarketWebsocket(HuobiWebsocket):

    def __init__(self, ws_url: str = HUOBI_WS_MARKET_URL):
        super().__init__(ws_url=ws_url)

    async def _pong(self, timestamp: int) -> None:
        await self.socket.send_json({'pong': timestamp})

    async def subscribe(self, stream: BaseMarketStream):
        for message in stream.subscribe():
            await self.socket.send_json(message)

    async def unsubscribe(self, stream: BaseMarketStream):
        for message in stream.unsubscribe():
            await self.socket.send_json(message)

    async def __aiter__(self) -> AsyncGenerator[Dict, None]:
        async for msg in self.socket:
            raw = msg.data  # type:ignore
            data = json.loads(gzip.decompress(raw))
            if 'ping' in data:
                await self._pong(data['ping'])
                continue
            yield data


class HuobiAccountOrderWebsocket(HuobiWebsocket):

    def __init__(
        self,
        ws_url: str = HUOBI_WS_ASSET_AND_ORDER_URL,
        access_key: str = HUOBI_ACCESS_KEY,
        secret_key: str = HUOBI_SECRET_KEY,
    ):
        super().__init__(ws_url=ws_url)
        self._access_key = access_key
        self._secret_key = secret_key

    async def __aenter__(self) -> 'HuobiAccountOrderWebsocket':
        await self.connect()
        await self.auth()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _pong(self, timestamp: int) -> None:
        msg = {
            'action': 'pong',
            'data': {
                'ts': timestamp,
            },
        }
        await self.socket.send_json(msg)

    async def auth(self) -> None:
        auth = WebsocketAuth(
            SecretKey=self._secret_key,
            accessKey=self._access_key,
        )
        msg = {
            'action': 'req',
            'ch': 'auth',
            'params': auth.to_request(self._ws_url, 'GET'),
        }
        await self.socket.send_json(msg)
        recv = await self.socket.receive_json()
        code = recv['code']
        if code != 200:
            raise WSHuobiError(
                err_code=code,
                err_msg=recv['message'],
            )

    async def __aiter__(self) -> AsyncGenerator[Dict, None]:
        async for msg in self.socket:
            raw = msg.data  # type:ignore
            data = json.loads(raw)
            if data.get('action', '') == 'ping':
                await self._pong(data['data']['ts'])
                continue
            yield data
