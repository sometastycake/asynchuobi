import gzip
import json
from typing import AsyncGenerator, Dict, Optional

import aiohttp
from aiohttp import WSMessage

from huobiclient.config import huobi_client_config as cfg
from huobiclient.exceptions import WsHuobiError


class BaseHuobiWebsocket:

    def __init__(self, ws_url: str):
        self._ws_url = ws_url
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
        )
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None

    def __del__(self) -> None:
        if self._session.connector and not self._session.closed:
            self._session.connector.close()

    async def _close(self) -> None:
        if self._ws is not None:
            await self._ws.close()
            await self._session.close()

    async def _connect(self) -> aiohttp.ClientWebSocketResponse:
        return await self._session.ws_connect(
            autoping=False,
            url=self._ws_url,
        )

    async def send(self, message: Dict) -> None:
        if self._ws is None:
            self._ws = await self._connect()
        await self._ws.send_json(message)

    @property
    def closed(self) -> bool:
        if self._ws is None:
            raise RuntimeError('WS is not initialized')
        return self._ws.closed


class HuobiMarketWebsocket(BaseHuobiWebsocket):

    def __init__(self, ws_url: str = cfg.HUOBI_WS_MARKET_URL):
        super().__init__(ws_url=ws_url)

    def _decode_msg(self, message: WSMessage) -> Dict:
        return json.loads(gzip.decompress(message.data))

    async def _send_pong(self, timestamp: int) -> None:
        await self.send({'pong': timestamp})

    def _check_error(self, message: Dict) -> None:
        if message.get('status', '') == 'error':
            raise WsHuobiError(
                err_code=message['err-code'],
                err_msg=message['err-msg'],
            )

    async def recv(self) -> AsyncGenerator[Dict, None]:
        if self._ws is None:
            raise RuntimeError('WS is not initialized')
        async for msg in self._ws:
            response: Dict = self._decode_msg(msg)  # type:ignore
            self._check_error(response)
            ping: Optional[int] = response.get('ping')
            if ping:
                await self._send_pong(ping)
                continue
            yield response


class HuobiAccountOrderWebsocket(BaseHuobiWebsocket):

    def __init__(self, ws_url: str = cfg.HUOBI_WS_ASSET_AND_ORDER_URL):
        super().__init__(ws_url=ws_url)

    def _decode_msg(self, message: WSMessage) -> Dict:
        return json.loads(message.data)

    async def _send_pong(self, timestamp: int) -> None:
        await self.send({
            'action': 'pong',
            'data': {
                'ts': timestamp,
            },
        })

    def _check_error(self, message: Dict) -> None:
        if message.get('code', -1) != 200:
            raise WsHuobiError(
                err_code=message['code'],
                err_msg=message['message'],
            )

    async def recv(self) -> AsyncGenerator[Dict, None]:
        if self._ws is None:
            raise RuntimeError('WS is not initialized')
        async for msg in self._ws:
            response: Dict = self._decode_msg(msg)  # type:ignore
            self._check_error(response)
            action: Optional[str] = response.get('action', '')
            if action == 'ping':
                await self._send_pong(response['data']['ts'])
                continue
            yield response
