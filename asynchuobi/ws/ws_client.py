import asyncio
import gzip
import json
import uuid
import warnings
from typing import Any, Awaitable, Callable, Dict, Optional, Set, Type, Union, cast

from aiohttp import WSMsgType

from asynchuobi.auth import WebsocketAuth
from asynchuobi.enums import CandleInterval
from asynchuobi.enums import MarketDepthAggregationLevel as Aggregation
from asynchuobi.exceptions import WSConnectionNotAuthorized, WSHuobiError
from asynchuobi.urls import HUOBI_WS_ACCOUNT_URL, HUOBI_WS_MARKET_URL
from asynchuobi.ws.enums import Subcription, WSTradeDetailMode
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


def _default_message_id() -> str:
    return str(uuid.uuid4())


class HuobiMarketWebsocket:
    """
    Websocket class for retrieving market data.

    Usage:

        async with HuobiMarketWebsocket() as ws:
            await ws.market_candlestick_stream('btcusdt', CandleInterval.min_1, SubUnsub.sub)
            await ws.market_detail_stream('ethusdt', SubUnsub.sub)
            async for message in ws:
                ...

    You can define callbacks which will called when message was received from Huobi websocket:

        def callback_market_detail(message: dict):
            print(message)

        async with HuobiMarketWebsocket() as ws:
            await ws.market_detail_stream(
                symbol='ethusdt',
                action=SubUnsub.sub,
                callback=callback_market_detail,
            )
            await ws.run_with_callbacks()

        You can also define async callback

    Parameters:
        url - Websocket url
        loads - Method of json deserialize (default json.loads)
        decompress - Method of gzip decompress (default gzip.decompress)
        default_message_id - Method of generating messages id
            Identifiers are sent in some messages, for example:
            {
                'sub': 'market.btcusdt.kline.1min',
                'id': 'id_example'
            }
        raise_if_error - Raise exception if error message was received from websocket
        run_callbacks_in_asyncio_tasks - If True, then callbacks are run into asyncio.create_task
        error_callback - Callback for error messages
        connection - Object for managing websocket connection
    """
    def __init__(
        self,
        url: str = HUOBI_WS_MARKET_URL,
        loads: LOADS_TYPE = json.loads,
        decompress: DECOMPRESS_TYPE = gzip.decompress,
        default_message_id: Callable[[], str] = _default_message_id,
        raise_if_error: bool = False,
        run_callbacks_in_asyncio_tasks: bool = True,
        error_callback: Optional[ERROR_CALLBACK_TYPE] = None,
        connection: Type[WebsocketConnectionAbstract] = WebsocketConnection,
        **connection_kwargs,
    ):
        if error_callback and not callable(error_callback):
            raise TypeError(f'Error callback {error_callback} is not callable')
        if raise_if_error and error_callback:
            raise ValueError('Cannot both specify raise_if_error and error_callback')
        self._loads = loads
        self._decompress = decompress
        self._connection = connection(url=url, **connection_kwargs)
        self._default_message_id = default_message_id
        self._raise_if_error = raise_if_error
        self._run_callbacks_in_asyncio_tasks = run_callbacks_in_asyncio_tasks
        self._subscribed_ch: Set[str] = set()
        self._callbacks: Dict[str, CALLBACK_TYPE] = {}
        self._error_callback = error_callback

    async def __aenter__(self):
        await self._connection.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._connection.close()

    async def _pong(self, timestamp: int) -> None:
        await self._connection.send({'pong': timestamp})

    async def _handler(
            self,
            topic: str,
            action: Subcription,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(action, Subcription):
            raise TypeError(f'Action type is not SubUnsub, received type "{type(action)}"')
        if action is Subcription.sub:
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
            action.value: topic,
        }
        if message_id is not None:
            message['id'] = message_id
        await self._connection.send(message)

    async def close(self) -> None:
        if not self._connection.closed:
            await self._connection.close()

    async def unsubscribe_all(self) -> None:
        if self._connection.closed:
            return
        for topic in self._subscribed_ch:
            await self._connection.send({'unsub': topic})
        self._subscribed_ch.clear()

    async def candlestick(
            self,
            symbol: str,
            interval: Union[CandleInterval, str],
            action: Subcription,
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
        await self._handler(
            topic=f'market.{symbol}.kline.{period}',
            action=action,
            callback=callback,
            message_id=message_id or self._default_message_id(),
        )

    async def ticker_info(
            self,
            symbol: str,
            action: Subcription,
            callback: Optional[CALLBACK_TYPE] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handler(
            topic=f'market.{symbol}.ticker',
            action=action,
            callback=callback,
        )

    async def orderbook(
            self,
            symbol: str,
            action: Subcription,
            level: Aggregation = Aggregation.step0,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handler(
            topic=f'market.{symbol}.depth.{level.value}',
            action=action,
            callback=callback,
            message_id=message_id or self._default_message_id(),
        )

    async def best_bid_offer(
            self,
            symbol: str,
            action: Subcription,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handler(
            topic=f'market.{symbol}.bbo',
            action=action,
            callback=callback,
            message_id=message_id or self._default_message_id(),
        )

    async def trade_detail(
            self,
            symbol: str,
            action: Subcription,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handler(
            topic=f'market.{symbol}.trade.detail',
            action=action,
            callback=callback,
            message_id=message_id or self._default_message_id(),
        )

    async def market_detail(
            self,
            symbol: str,
            action: Subcription,
            callback: Optional[CALLBACK_TYPE] = None,
            message_id: Optional[str] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handler(
            topic=f'market.{symbol}.detail',
            action=action,
            callback=callback,
            message_id=message_id or self._default_message_id(),
        )

    async def etp(
            self,
            symbol: str,
            action: Subcription,
            callback: Optional[CALLBACK_TYPE] = None,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError(f'Symbol is not str, received type "{type(symbol)}"')
        await self._handler(
            topic=f'market.{symbol}.etp',
            action=action,
            callback=callback,
        )

    def __aiter__(self) -> 'HuobiMarketWebsocket':
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
            data = self._loads(self._decompress(message.data))
            ping = data.get('ping')
            if ping:
                await self._pong(ping)
                continue
            status = data.get('status') or ''
            if status == 'error' and self._raise_if_error:
                raise WSHuobiError(
                    err_code=data['err-code'],
                    err_msg=data['err-msg'],
                )
            return data

    async def _run_callback(
            self,
            callback: Union[CALLBACK_TYPE, ERROR_CALLBACK_TYPE],
            data: Any,
    ) -> None:
        if asyncio.iscoroutinefunction(callback):
            if self._run_callbacks_in_asyncio_tasks:
                asyncio.create_task(callback(data))
            else:
                await callback(data)
        else:
            callback(data)

    async def run_with_callbacks(self) -> None:
        if not self._callbacks:
            warnings.warn('Callbacks not specified')
            return
        async for message in self:
            message = cast(WS_MESSAGE_TYPE, message)
            status = message.get('status') or ''
            if status == 'error' and self._error_callback:
                error = WSHuobiError(
                    err_code=message['err-code'],
                    err_msg=message['err-msg'],
                )
                await self._run_callback(
                    callback=self._error_callback,
                    data=error,
                )
                continue
            channel = message.get('ch') or message.get('subbed')
            if not channel:
                continue
            await self._run_callback(
                callback=self._callbacks[channel],
                data=message,
            )


class HuobiAccountWebsocket:
    """
    Websocket class for retrieving information about orders and account.

    Usage:

        async with HuobiAccountWebsocket(
            access_key='access_key',
            secret_key='secret_key',
        ) as ws:
            await ws.subscribe_account_change()
            await ws.subscribe_order_updates('btcusdt')
            async for message in ws:
                ...

    You can define callbacks which will called when message was received from Huobi websocket:

        def callback_balance_update(message):
            print(message)

        async with HuobiAccountWebsocket(
            access_key='access_key',
            secret_key='secret_key',
        ) as ws:
            await ws.subscribe_account_change(
                callback=callback_balance_update,
            )
            await ws.run_with_callbacks()

        You can also define async callback

    Parameters:
        access_key - Access key
        secret_key - Secret key
        url - Websocket url
        loads - Method of json deserialize (default json.loads)
        raise_if_error - Raise exception if error message was received from websocket
        run_callbacks_in_asyncio_tasks - If True, then callbacks run into asyncio.create_task
        connection - Object for managing websocket connection
    """
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        url: str = HUOBI_WS_ACCOUNT_URL,
        loads: LOADS_TYPE = json.loads,
        raise_if_error: bool = False,
        run_callbacks_in_asyncio_tasks: bool = True,
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
        self._is_auth = False
        self._raise_if_error = raise_if_error
        self._callbacks: Dict[str, CALLBACK_TYPE] = {}
        self._run_callbacks_in_asyncio_tasks = run_callbacks_in_asyncio_tasks

    async def __aenter__(self) -> 'HuobiAccountWebsocket':
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
        """
        Authenticate the connection.
        """
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
        else:
            self._is_auth = True

    async def subscribe(self, topic: str, callback: Optional[CALLBACK_TYPE] = None) -> None:
        """
        Subscribe to topic.
        """
        if not self._is_auth:
            raise WSConnectionNotAuthorized('Connection is not authorized')
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

    def __aiter__(self) -> 'HuobiAccountWebsocket':
        return self

    async def __anext__(self) -> WS_MESSAGE_TYPE:
        while True:
            message = await self._connection.receive()
            if message.type in _CLOSING_STATUSES:
                raise StopAsyncIteration
            data = self._loads(message.data)
            action = data.get('action') or ''
            if action == 'ping':
                await self._pong(data['data']['ts'])
                continue
            code = data.get('code')
            if code and code != 200 and self._raise_if_error:
                raise WSHuobiError(
                    err_code=code,
                    err_msg=data['message'],
                )
            return data

    async def run_with_callbacks(self) -> None:
        if not self._callbacks:
            warnings.warn('Callbacks not specified')
            return
        async for message in self:
            message = cast(WS_MESSAGE_TYPE, message)
            channel = message['ch']
            callback = self._callbacks[channel]
            if asyncio.iscoroutinefunction(callback):
                if self._run_callbacks_in_asyncio_tasks:
                    asyncio.create_task(callback(message))
                else:
                    await callback(message)
            else:
                callback(message)
