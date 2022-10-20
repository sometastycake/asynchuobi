from typing import Optional

from aiohttp import ClientSession, ClientWebSocketResponse, TCPConnector

from huobiclient.auth import WebsocketAuth
from huobiclient.config import huobi_client_config as cfg


class HuobiWebsocket:

    def __init__(self, ws_url: str):
        self._ws_url = ws_url
        self._session: Optional[ClientSession] = None
        self._ws: Optional[ClientWebSocketResponse] = None

    @property
    def ws(self) -> ClientWebSocketResponse:
        if self._ws is None:
            raise RuntimeError('WS is not initialized')
        return self._ws

    async def close(self) -> None:
        if self._ws is not None and not self._ws.closed:
            await self._ws.close()
        if self._session and not self._session.closed:
            await self._session.close()

    async def connect(self) -> None:
        self._session = ClientSession(
            connector=TCPConnector(ssl=False),
        )
        self._ws = await self._session.ws_connect(
            autoping=False,
            url=self._ws_url,
        )


class HuobiMarketWebsocket(HuobiWebsocket):

    def __init__(self, ws_url: str = cfg.HUOBI_WS_MARKET_URL):
        super().__init__(ws_url=ws_url)

    async def pong(self, timestamp: int) -> None:
        await self.ws.send_json({'pong': timestamp})


class HuobiAccountOrderWebsocket(HuobiWebsocket):

    def __init__(self, ws_url: str = cfg.HUOBI_WS_ASSET_AND_ORDER_URL):
        super().__init__(ws_url=ws_url)

    async def pong(self, timestamp: int) -> None:
        await self.ws.send_json({
            'action': 'pong',
            'data': {
                'ts': timestamp,
            },
        })

    async def auth(self) -> None:
        await self.ws.send_json({
            'action': 'req',
            'ch': 'auth',
            'params': WebsocketAuth().to_request(),
        })
