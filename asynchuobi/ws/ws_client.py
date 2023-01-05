import asyncio
import gzip
import json
from typing import Any, Awaitable, Callable, Dict, Optional, Set, Type, Union, cast

from aiohttp import WSMsgType

from asynchuobi.auth import WebsocketAuth
from asynchuobi.enums import CandleInterval, DepthLevel
from asynchuobi.exceptions import WSAuthenticateError, WSHuobiError, WSNotAuthenticated
from asynchuobi.urls import HUOBI_WS_ACCOUNT_URL, HUOBI_WS_MARKET_URL
from asynchuobi.ws.enums import WSTradeDetailMode
from asynchuobi.ws.ws_connection import WS_MESSAGE_TYPE, WebsocketConnection, WebsocketConnectionAbstract

LOADS_TYPE = Callable[[Union[str, bytes]], Any]
DECOMPRESS_TYPE = Callable[[bytes], Union[str, bytes]]

CALLBACK_TYPE = Union[
    Callable[[WS_MESSAGE_TYPE], Awaitable[Any]],
    Callable[[WS_MESSAGE_TYPE], Any],
]

ERROR_CALLBACK_TYPE = Union[
    Callable[[WSHuobiError], Awaitable[Any]],
    Callable[[WSHuobiError], Any],
]

_CLOSING_STATUSES = (
    WSMsgType.CLOSE,
    WSMsgType.CLOSING,
    WSMsgType.CLOSED,
)


def _is_async__call__(callback: Union[CALLBACK_TYPE, ERROR_CALLBACK_TYPE]) -> bool:
    return (
        type(type(callback)) is type and
        hasattr(callback, '__call__') and
        asyncio.iscoroutinefunction(callback.__call__)
    )


class _base_stream:

    def __init__(self, ws: 'WSHuobiMarket', symbol: str):
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol {symbol} is not str')
        self._ws = ws
        self._symbol = symbol

    @property
    def topic(self) -> str:
        raise NotImplementedError

    async def sub(self, callback: Optional[CALLBACK_TYPE] = None):
        await self._ws.send_message_handler(
            topic=self.topic,
            action='sub',
            callback=callback,
        )

    async def unsub(self):
        await self._ws.send_message_handler(
            topic=self.topic,
            action='unsub',
        )


class _candles(_base_stream):

    def __init__(self, ws: 'WSHuobiMarket', symbol: str, interval: str):
        super().__init__(ws, symbol)
        self._interval = interval

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.kline.{self._interval}'


class _market_ticker_info(_base_stream):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.ticker'


class _orderbook(_base_stream):

    def __init__(self, ws: 'WSHuobiMarket', symbol: str, level: DepthLevel):
        super().__init__(ws, symbol)
        self._level = level

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.depth.{self._level.value}'


class _best_bid_offer(_base_stream):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.bbo'


class _latest_trades(_base_stream):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.trade.detail'


class _market_stats(_base_stream):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.detail'


class WSHuobiMarket:
    def __init__(
        self,
        url: str = HUOBI_WS_MARKET_URL,
        loads: LOADS_TYPE = json.loads,
        decompress: DECOMPRESS_TYPE = gzip.decompress,
        run_callbacks_in_asyncio_tasks: bool = False,
        connection: Type[WebsocketConnectionAbstract] = WebsocketConnection,
        **connection_kwargs,
    ):
        self._loads = loads
        self._decompress = decompress
        self._connection = connection(url=url, **connection_kwargs)
        self._run_callbacks_in_asyncio_tasks = run_callbacks_in_asyncio_tasks
        self._subscribed_ch: Set[str] = set()
        self._callbacks: Dict[str, CALLBACK_TYPE] = {}

    async def __aenter__(self):
        await self._connection.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._connection.close()

    async def _pong(self, timestamp: int) -> None:
        await self._connection.send({'pong': timestamp})

    async def send_message_handler(
            self,
            topic: str,
            action: str,
            callback: Optional[CALLBACK_TYPE] = None,
    ) -> None:
        if action == 'sub':
            self._subscribed_ch.add(topic)
            if callback:
                if not callable(callback):
                    raise TypeError(f'Object {callback} is not callable')
                self._callbacks[topic] = callback
        else:
            if topic in self._callbacks:
                del self._callbacks[topic]
            self._subscribed_ch.discard(topic)
        message = {
            action: topic,
        }
        await self._connection.send(message)

    async def close(self) -> None:
        if not self._connection.closed:
            await self._connection.close()

    def candlestick(self, symbol: str, interval: Union[CandleInterval, str]) -> _candles:
        """This topic sends a new candlestick whenever it is available."""
        if isinstance(interval, CandleInterval):
            period = str(interval.value)
        elif isinstance(interval, str):
            period = interval
        else:
            raise TypeError(f'Wrong type "{type(interval)}" for interval')
        return _candles(
            ws=self, symbol=symbol, interval=period,
        )

    def market_ticker_info(self, symbol: str) -> _market_ticker_info:
        """Retrieve the market ticker,data is pushed every 100ms."""
        return _market_ticker_info(ws=self, symbol=symbol)

    def orderbook(self, symbol: str, level: DepthLevel = DepthLevel.step0) -> _orderbook:
        """This topic sends the latest market by price order book."""
        return _orderbook(ws=self, symbol=symbol, level=level)

    def best_bid_offer(self, symbol: str) -> _best_bid_offer:
        """User can receive BBO (Best Bid/Offer) update in tick by tick mode."""
        return _best_bid_offer(ws=self, symbol=symbol)

    def latest_trades(self, symbol: str) -> _latest_trades:
        """This topic sends the latest completed trades."""
        return _latest_trades(ws=self, symbol=symbol)

    def market_stats(self, symbol: str) -> _market_stats:
        """This topic sends the latest market stats with 24h summary."""
        return _market_stats(ws=self, symbol=symbol)

    def __aiter__(self) -> 'WSHuobiMarket':
        return self

    async def __anext__(self) -> WS_MESSAGE_TYPE:
        while True:
            message = await self._connection.receive()
            if message.type in _CLOSING_STATUSES:
                if not self._connection.closed and self._subscribed_ch:
                    await self._connection.connect()
                    for topic in self._subscribed_ch:
                        await self._connection.send({'sub': topic})
                    continue
                raise StopAsyncIteration
            payload = self._loads(self._decompress(message.data))
            ping = payload.get('ping')
            if ping:
                await self._pong(ping)
                continue
            return payload

    async def _exec_callback(
            self,
            callback: Union[CALLBACK_TYPE, ERROR_CALLBACK_TYPE],
            data: Any,
    ) -> None:
        if asyncio.iscoroutinefunction(callback) or _is_async__call__(callback):
            if self._run_callbacks_in_asyncio_tasks:
                asyncio.create_task(callback(data))  # type:ignore[arg-type]
            else:
                await callback(data)
        else:
            callback(data)

    async def run_with_callbacks(self, error_callback: ERROR_CALLBACK_TYPE) -> None:
        if not callable(error_callback):
            raise TypeError(f'Callback {error_callback} is not callable')
        async for message in self:
            message = cast(WS_MESSAGE_TYPE, message)
            status = message.get('status') or ''
            if status == 'error':
                error = WSHuobiError(
                    err_code=message['err-code'],
                    err_msg=message['err-msg'],
                )
                await self._exec_callback(error_callback, error)
                continue
            if 'ch' in message:
                topic = message['ch']
            elif 'subbed' in message:
                topic = message['subbed']
            elif 'unsubbed' in message:
                topic = message['unsubbed']
            else:
                raise ValueError(f'Not found topic in {message}')
            if topic not in self._callbacks:
                raise ValueError(f'Not specified callback for topic "{topic}"')
            await self._exec_callback(
                callback=self._callbacks[topic],
                data=message,
            )


class WSHuobiAccount:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        url: str = HUOBI_WS_ACCOUNT_URL,
        loads: LOADS_TYPE = json.loads,
        run_callbacks_in_asyncio_tasks: bool = False,
        connection: Type[WebsocketConnectionAbstract] = WebsocketConnection,
        **connection_kwargs,
    ):
        if not access_key or not secret_key:
            raise ValueError('Access key or secret key can not be empty')
        self._url = url
        self._loads = loads
        self._access_key = access_key
        self._secret_key = secret_key
        self._connection = connection(url=url, **connection_kwargs)
        self._is_auth = False
        self._callbacks: Dict[str, CALLBACK_TYPE] = {}
        self._run_callbacks_in_asyncio_tasks = run_callbacks_in_asyncio_tasks

    async def __aenter__(self) -> 'WSHuobiAccount':
        await self._connection.connect()
        await self.authorize()
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

    async def close(self) -> None:
        if not self._connection.closed:
            await self._connection.close()

    async def authorize(self) -> None:
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
            raise WSAuthenticateError(
                err_code=code,
                err_msg=data['message'],
            )
        else:
            self._is_auth = True

    async def subscribe(self, topic: str, callback: Optional[CALLBACK_TYPE] = None) -> None:
        if not self._is_auth:
            raise WSNotAuthenticated('Connection is not authorized')
        if callback:
            if not callable(callback):
                raise TypeError(f'Object {callback} is not callable')
            self._callbacks[topic] = callback
        await self._connection.send({
            'action': 'sub',
            'ch': topic,
        })

    async def subscribe_order_updates(
            self,
            symbol: str,
            callback: Optional[CALLBACK_TYPE] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self.subscribe(
            topic=f'orders#{symbol}',
            callback=callback,
        )

    async def subscribe_trade_detail(
            self,
            symbol: str,
            mode: WSTradeDetailMode = WSTradeDetailMode.only_trade_event,
            callback: Optional[CALLBACK_TYPE] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self.subscribe(
            topic=f'trade.clearing#{symbol}#{mode.value}',
            callback=callback,
        )

    async def subscribe_account_change(
            self,
            mode: int = 0,
            callback: Optional[CALLBACK_TYPE] = None,
    ) -> None:
        if mode not in (0, 1, 2):
            raise ValueError('Wrong mode value')
        await self.subscribe(
            topic=f'accounts.update#{mode}',
            callback=callback,
        )

    def __aiter__(self) -> 'WSHuobiAccount':
        return self

    async def __anext__(self) -> WS_MESSAGE_TYPE:
        while True:
            message = await self._connection.receive()
            if message.type in _CLOSING_STATUSES:
                raise StopAsyncIteration
            payload = self._loads(message.data)
            action = payload.get('action') or ''
            if action == 'ping':
                await self._pong(payload['data']['ts'])
                continue
            return payload

    async def _exec_callback(
            self,
            callback: Union[CALLBACK_TYPE, ERROR_CALLBACK_TYPE],
            data: Any,
    ) -> None:
        if asyncio.iscoroutinefunction(callback) or _is_async__call__(callback):
            if self._run_callbacks_in_asyncio_tasks:
                asyncio.create_task(callback(data))  # type:ignore[arg-type]
            else:
                await callback(data)
        else:
            callback(data)

    async def run_with_callbacks(self, error_callback: ERROR_CALLBACK_TYPE) -> None:
        if not callable(error_callback):
            raise TypeError(f'Callback {error_callback} is not callable')
        async for message in self:
            message = cast(WS_MESSAGE_TYPE, message)
            code = message.get('code')
            if code and code != 200:
                error = WSHuobiError(
                    err_code=code,
                    err_msg=message['message'],
                )
                await self._exec_callback(error_callback, error)
                continue
            topic = message['ch']
            if topic not in self._callbacks:
                raise ValueError(f'Not specified callback for topic "{topic}"')
            await self._exec_callback(
                callback=self._callbacks[topic],
                data=message,
            )
