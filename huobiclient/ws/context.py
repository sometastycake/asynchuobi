from typing import Any, AsyncGenerator, Dict, List, Optional, TypeVar, Union, cast

from aiohttp import WSMessage

from huobiclient.ws.client import HuobiAccountOrderWebsocket, HuobiMarketWebsocket
from huobiclient.ws.handlers.abstract import AbstractWebsocketMessageHandler
from huobiclient.ws.handlers.handlers import MarketWebsocketMessageHandler
from huobiclient.ws.request.abstract import AbstractWebsocketRequest

BaseRequestModelType = TypeVar(
    'BaseRequestModelType',
    bound=AbstractWebsocketRequest,
)


class WebsocketMarketContextManager:

    def __init__(
        self,
        ws: HuobiMarketWebsocket,
        request: Union[BaseRequestModelType, List[BaseRequestModelType]],
        handler: AbstractWebsocketMessageHandler = MarketWebsocketMessageHandler(),
    ):
        self._websocket: HuobiMarketWebsocket = ws
        self._request: List[BaseRequestModelType] = request if isinstance(request, list) else [request]
        self._handler = handler

    async def __aenter__(self) -> 'WebsocketMarketContextManager':
        await self._websocket.connect()
        for request in self._request:
            await self._websocket.ws.send_json(request.subscribe())
        return self

    async def __aexit__(self, exc_type, exc_vval, exc_tb) -> None:  # noqa:U100
        if self._websocket.ws.closed:
            return
        for request in self._request:
            await self._websocket.ws.send_json(request.unsubscribe())
        await self._websocket.close()

    async def __aiter__(self) -> AsyncGenerator[Any, None]:
        async for message in self._websocket.ws:
            message = cast(WSMessage, message)
            timestamp: Optional[int] = self._handler.is_ping(message)
            if timestamp:
                await self._websocket.pong(timestamp)
                continue
            yield self._handler(message)


class WebsocketAccountOrderContextManager:

    def __init__(
        self,
        ws: HuobiAccountOrderWebsocket,
        request: Union[BaseRequestModelType, List[BaseRequestModelType]],
        handler: AbstractWebsocketMessageHandler,
    ):
        self._websocket: HuobiAccountOrderWebsocket = ws
        self._request: List[BaseRequestModelType] = request if isinstance(request, list) else [request]
        self._handler = handler

    async def __aenter__(self) -> 'WebsocketAccountOrderContextManager':
        await self._websocket.connect()
        await self._websocket.auth()
        message: Dict = await self._websocket.ws.receive_json()
        self._handler.check_error(message)
        for request in self._request:
            await self._websocket.ws.send_json(request.subscribe())
        return self

    async def __aexit__(self, exc_type, exc_vval, exc_tb) -> None:  # noqa:U100
        if self._websocket.ws.closed:
            return
        for request in self._request:
            await self._websocket.ws.send_json(request.unsubscribe())

    async def __aiter__(self) -> AsyncGenerator[Any, None]:
        async for message in self._websocket.ws:
            message = cast(WSMessage, message)
            timestamp: Optional[int] = self._handler.is_ping(message)
            if timestamp:
                await self._websocket.pong(timestamp)
                continue
            yield self._handler(message)
