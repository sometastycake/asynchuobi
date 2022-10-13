import gzip
import json
from typing import AsyncGenerator, Dict, Optional

import aiohttp
from aiohttp import WSMessage

from huobiclient.exceptions import WsHuobiError


class HuobiWebsocket:

    def __init__(self, ws_url: str):
        self._ws_url = ws_url
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
        )
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None

    def __del__(self) -> None:
        if self._session.connector and not self._session.closed:
            self._session.connector.close()

    async def __aenter__(self) -> 'HuobiWebsocket':
        self._ws = await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa:U100
        await self._close()

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

    def _decode_msg(self, msg: WSMessage, decompress: bool = False) -> Dict:
        if decompress:
            return json.loads(gzip.decompress(msg.data))
        return json.loads(msg.data)

    def _check_message_error(self, response: Dict) -> None:
        if response.get('status', '') == 'error':
            raise WsHuobiError(
                err_code=response['err-code'],
                err_msg=response['err-msg'],
            )

    async def _pong(self, value: int) -> None:
        if self._ws is None:
            raise RuntimeError('WS is not initialized')
        await self._ws.send_json({'pong': value})

    async def recv(self, decompress: bool = False) -> AsyncGenerator[Dict, None]:
        if self._ws is None:
            raise RuntimeError('WS is not initialized')
        async for msg in self._ws:
            response: Dict = self._decode_msg(msg, decompress)  # type:ignore
            self._check_message_error(response)
            ping = response.get('ping')
            if ping:
                await self._pong(ping)
                continue
            yield response
