import asyncio
import gzip
import json
import uuid
from typing import Any, Awaitable, Callable, Dict, Optional, Set, Type, Union, cast

from aiohttp import WSMsgType

from asynchuobi.auth import WebsocketAuth
from asynchuobi.enums import CandleInterval
from asynchuobi.enums import MarketDepthAggregationLevel as Aggregation
from asynchuobi.exceptions import WSHuobiError
from asynchuobi.urls import HUOBI_WS_ASSET_AND_ORDER_URL, HUOBI_WS_MARKET_URL
from asynchuobi.ws.enums import SubUnsub, WSTradeDetailMode
from asynchuobi.ws.topics import (
    bbo_topic,
    etp_topic,
    market_candlestick_topic,
    market_depth_topic,
    market_detail_topic,
    ticker_topic,
    trade_detail_topic,
)
from asynchuobi.ws.ws_connection import WebsocketConnection

LOADS_TYPE = Callable[[Union[str, bytes]], Any]

DECOMPRESS_TYPE = Callable[[bytes], Union[str, bytes]]

CALLBACK_TYPE = Union[
    Callable[[Dict], Awaitable[Any]],
    Callable[[Dict], Any]
]

_CLOSING_STATUSES = (
    WSMsgType.CLOSE,
    WSMsgType.CLOSING,
    WSMsgType.CLOSED,
)


def _default_message_id() -> str:
    return str(uuid.uuid4())


class HuobiMarketWebsocket:

    def __init__(
        self,
        url: str = HUOBI_WS_MARKET_URL,
        loads: LOADS_TYPE = json.loads,
        decompress: DECOMPRESS_TYPE = gzip.decompress,
        default_message_id: Callable[..., str] = _default_message_id,
        connection: Type[WebsocketConnection] = WebsocketConnection,
        **connection_kwargs,
    ):
        self._loads = loads
        self._decompress = decompress
        self._connection = connection(url=url, **connection_kwargs)
        self._default_message_id = default_message_id
        self._subscribed_ch: Set[str] = set()
        self._callbacks: Dict[str, CALLBACK_TYPE] = {}

    async def __aenter__(self):
        await self._connection.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._connection.close()

    async def _pong(self, timestamp: int) -> None:
        await self._connection.send({'pong': timestamp})

    async def _handle_sub_unsub(
            self,
            topic: str,
            action: SubUnsub,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(action, SubUnsub):
            raise TypeError(f'Action type is not SubUnsub, received type "{type(action)}"')
        message = {
            action.value: topic,
        }
        if message_id is not None:
            message['id'] = message_id
        await self._connection.send(message)
        if action is SubUnsub.sub:
            self._subscribed_ch.add(topic)
            if callback:
                if not callable(callback):
                    raise TypeError(f'Object {callback} is not callable')
                self._callbacks[topic] = callback
        else:
            self._subscribed_ch.discard(topic)

    async def market_candlestick_stream(
            self,
            symbol: str,
            interval: Union[CandleInterval, str],
            action: SubUnsub,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        if isinstance(interval, CandleInterval):
            period = interval.value
        elif isinstance(interval, str):
            period = interval
        else:
            raise TypeError(f'Wrong type "{type(interval)}" for interval')
        await self._handle_sub_unsub(
            topic=market_candlestick_topic(symbol, period),
            action=action,
            callback=callback,
            message_id=message_id or self._default_message_id(),
        )

    async def ticker_stream(
            self,
            symbol: str,
            action: SubUnsub,
            callback: Optional[CALLBACK_TYPE] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handle_sub_unsub(
            topic=ticker_topic(symbol),
            action=action,
            callback=callback,
        )

    async def market_depth_stream(
            self,
            symbol: str,
            action: SubUnsub,
            aggregation_level: Aggregation = Aggregation.step0,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handle_sub_unsub(
            topic=market_depth_topic(symbol, aggregation_level),
            action=action,
            callback=callback,
            message_id=message_id or self._default_message_id(),
        )

    async def best_bid_offer_stream(
            self,
            symbol: str,
            action: SubUnsub,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handle_sub_unsub(
            topic=bbo_topic(symbol),
            action=action,
            callback=callback,
            message_id=message_id or self._default_message_id(),
        )

    async def trade_detail_stream(
            self,
            symbol: str,
            action: SubUnsub,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handle_sub_unsub(
            topic=trade_detail_topic(symbol),
            action=action,
            callback=callback,
            message_id=message_id or self._default_message_id(),
        )

    async def market_detail_stream(
            self,
            symbol: str,
            action: SubUnsub,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handle_sub_unsub(
            topic=market_detail_topic(symbol),
            action=action,
            callback=callback,
            message_id=message_id or self._default_message_id(),
        )

    async def etp_stream(
            self,
            symbol: str,
            action: SubUnsub,
            callback: Optional[CALLBACK_TYPE] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handle_sub_unsub(
            topic=etp_topic(symbol),
            action=action,
            callback=callback,
        )

    def __aiter__(self) -> 'HuobiMarketWebsocket':
        return self

    async def __anext__(self) -> Dict:
        while True:
            message = await self._connection.receive()
            if message.type in _CLOSING_STATUSES:
                if not self._connection.closed and self._subscribed_ch:
                    await self._connection.connect()
                    for topic in self._subscribed_ch:
                        await self._connection.send({'sub': topic})
                    continue
                raise StopAsyncIteration
            data = self._loads(self._decompress(message.data))
            if 'ping' in data:
                await self._pong(data['ping'])
                continue
            return data

    async def run_with_callbacks(self) -> None:
        if not self._callbacks:
            raise RuntimeError('Callbacks not specified')
        async for message in self:
            message = cast(dict, message)
            channel = message.get('ch') or message.get('subbed')
            if channel:
                if channel not in self._callbacks:
                    continue
                callback = self._callbacks[channel]
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(message))
                else:
                    callback(message)


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
        if not access_key or not secret_key:
            raise ValueError('Access key or secret key can not be empty')
        self._url = url
        self._loads = loads
        self._access_key = access_key
        self._secret_key = secret_key
        self._connection = connection(url=url, **connection_kwargs)

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

    async def send(self, message: Dict) -> None:
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
        data = self._loads(recv.data)
        code = data['code']
        if code != 200:
            raise WSHuobiError(
                err_code=code,
                err_msg=data['message'],
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
            mode: WSTradeDetailMode = WSTradeDetailMode.only_trade_event,
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

    def __aiter__(self) -> 'HuobiAccountOrderWebsocket':
        return self

    async def __anext__(self) -> Dict:
        while True:
            message = await self._connection.receive()
            if message.type in _CLOSING_STATUSES:
                raise StopAsyncIteration
            data = self._loads(message.data)
            if data.get('action', '') == 'ping':
                await self._pong(data['data']['ts'])
                continue
            return data
