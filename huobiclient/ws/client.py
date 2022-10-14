import gzip
import json
from typing import AsyncGenerator, Dict, Optional

import aiohttp
from aiohttp import WSMessage

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

    def _check_message_error(self, response: Dict) -> None:
        if response.get('status', '') == 'error':
            raise WsHuobiError(
                err_code=response['err-code'],
                err_msg=response['err-msg'],
            )


class HuobiMarketWebsocket(BaseHuobiWebsocket):

    def _decode_msg(self, msg: WSMessage) -> Dict:
        return json.loads(gzip.decompress(msg.data))

    async def _pong(self, value: int) -> None:
        await self.send({'pong': value})

    async def recv(self) -> AsyncGenerator[Dict, None]:
        if self._ws is None:
            raise RuntimeError('WS is not initialized')
        async for msg in self._ws:
            response: Dict = self._decode_msg(msg)  # type:ignore
            self._check_message_error(response)
            ping = response.get('ping')
            if ping:
                await self._pong(ping)
                continue
            yield response


class HuobiAccountOrderWebsocket(BaseHuobiWebsocket):

    def _decode_msg(self, msg: WSMessage) -> Dict:
        return json.loads(msg.data)

    async def _pong(self, timestamp: int) -> None:
        await self.send({
            'action': 'pong',
            'data': {
                'ts': timestamp,
            },
        })

    async def recv(self) -> AsyncGenerator[Dict, None]:
        if self._ws is None:
            raise RuntimeError('WS is not initialized')
        async for msg in self._ws:
            response: Dict = self._decode_msg(msg)  # type:ignore
            self._check_message_error(response)
            action = response.get('action', '')
            if action == 'ping':
                await self._pong(response['data']['ts'])
                continue
            yield response
