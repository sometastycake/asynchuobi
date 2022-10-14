from typing import AsyncGenerator, List, Type, TypeVar, Union, cast

from pydantic import BaseModel

from huobiclient.schemas.ws.abstract import AbstractWebsocketRequest
from huobiclient.schemas.ws.market.response import (
    MarketBestBidOfferResponse,
    MarketByPriceRefreshUpdateResponse,
    MarketCandleResponse,
    MarketDetailResponse,
    MarketEtpRealTimeNavResponse,
    MarketOrderbookResponse,
    MarketTickerResponse,
    MarketTradeDetailResponse,
)
from huobiclient.ws.client import HuobiMarketWebsocket

BaseRequestModel = TypeVar('BaseRequestModel', bound=AbstractWebsocketRequest)


class WebsocketContextManager:

    def __init__(
        self,
        ws: HuobiMarketWebsocket,
        request: Union[BaseRequestModel, List[BaseRequestModel]],
        response: Type[BaseModel],
    ):
        self._ws = ws
        self._request = request if isinstance(request, list) else [request]
        self._response = response

    async def __aenter__(self) -> 'WebsocketContextManager':
        for request in self._request:
            await self._ws.send(request.subscribe())
        return self

    async def __aexit__(self, exc_type, exc_vval, exc_tb) -> None:  # noqa:U100
        for request in self._request:
            if not self._ws.closed:
                await self._ws.send(request.unsubscribe())

    async def __aiter__(self) -> AsyncGenerator[BaseModel, None]:
        async for msg in self._ws.recv():
            if 'ch' not in msg:
                continue
            yield self._response.parse_obj(msg)


class _WebsocketContextManager_MarketTickerResponse(WebsocketContextManager):  # noqa

    async def __aiter__(self) -> AsyncGenerator[MarketTickerResponse, None]:
        async for msg in super().__aiter__():
            yield cast(MarketTickerResponse, msg)


class _WebsocketContextManager_MarketCandleResponse(WebsocketContextManager):  # noqa

    async def __aiter__(self) -> AsyncGenerator[MarketCandleResponse, None]:
        async for msg in super().__aiter__():
            yield cast(MarketCandleResponse, msg)


class _WebsocketContextManager_MarketOrderbookResponse(WebsocketContextManager):  # noqa

    async def __aiter__(self) -> AsyncGenerator[MarketOrderbookResponse, None]:
        async for msg in super().__aiter__():
            yield cast(MarketOrderbookResponse, msg)


class _WebsocketContextManager_MarketDetailResponse(WebsocketContextManager):  # noqa

    async def __aiter__(self) -> AsyncGenerator[MarketDetailResponse, None]:
        async for msg in super().__aiter__():
            yield cast(MarketDetailResponse, msg)


class _WebsocketContextManager_MarketTradeDetailResponse(WebsocketContextManager):  # noqa

    async def __aiter__(self) -> AsyncGenerator[MarketTradeDetailResponse, None]:
        async for msg in super().__aiter__():
            yield cast(MarketTradeDetailResponse, msg)


class _WebsocketContextManager_MarketBestBidOfferResponse(WebsocketContextManager):  # noqa

    async def __aiter__(self) -> AsyncGenerator[MarketBestBidOfferResponse, None]:
        async for msg in super().__aiter__():
            yield cast(MarketBestBidOfferResponse, msg)

class _WebsocketContextManager_MarketEtpRealTimeNavResponse(WebsocketContextManager):  # noqa

    async def __aiter__(self) -> AsyncGenerator[MarketEtpRealTimeNavResponse, None]:
        async for msg in super().__aiter__():
            yield cast(MarketEtpRealTimeNavResponse, msg)

class _WebsocketContextManager_MarketByPriceRefreshUpdateResponse(WebsocketContextManager):  # noqa

    async def __aiter__(self) -> AsyncGenerator[MarketByPriceRefreshUpdateResponse, None]:
        async for msg in super().__aiter__():
            yield cast(MarketByPriceRefreshUpdateResponse, msg)
