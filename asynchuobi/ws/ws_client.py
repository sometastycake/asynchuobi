import gzip
import json
from typing import Any, Callable, Dict, Set, Type, Union

from aiohttp import WSMsgType

from asynchuobi.auth import WebsocketAuth
from asynchuobi.enums import CandleInterval
from asynchuobi.enums import MarketDepthAggregationLevel as Aggregation
from asynchuobi.exceptions import WSHuobiError
from asynchuobi.urls import HUOBI_WS_ASSET_AND_ORDER_URL, HUOBI_WS_MARKET_URL
from asynchuobi.ws.ws_connection import WebsocketConnection
from asynchuobi.ws.ws_enums import SubUnsub, WSTradeDetailMode

LOADS_TYPE = Callable[[Union[str, bytes]], Any]

_CLOSING_STATUSES = (
    WSMsgType.CLOSE,
    WSMsgType.CLOSING,
    WSMsgType.CLOSED,
)


class HuobiMarketWebsocket:

    def __init__(
        self,
        url: str = HUOBI_WS_MARKET_URL,
        loads: LOADS_TYPE = json.loads,
        decompress: Callable[[bytes], Union[str, bytes]] = gzip.decompress,
        connection: Type[WebsocketConnection] = WebsocketConnection,
        **connection_kwargs,
    ):
        self._loads = loads
        self._decompress = decompress
        self._connection = connection(url=url, **connection_kwargs)
        self._subscribed_ch: Set[str] = set()

    async def __aenter__(self):
        await self._connection.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._connection.close()

    async def _pong(self, timestamp: int) -> None:
        await self._connection.send({'pong': timestamp})

    async def send(self, message: Dict) -> None:
        await self._connection.send(message)

    async def _handle_sub_unsub(self, topic: str, action: SubUnsub):
        if not isinstance(action, SubUnsub):
            raise TypeError('Action type is not SubUnsub')
        await self._connection.send({
            action.value: topic,
        })
        if action is SubUnsub.sub:
            self._subscribed_ch.add(topic)
        else:
            self._subscribed_ch.discard(topic)

    async def market_candlestick_stream(
            self,
            symbol: str,
            interval: Union[CandleInterval, str],
            action: SubUnsub,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError('Symbol is not str')
        if isinstance(interval, CandleInterval):
            interval_ = interval.value
        elif isinstance(interval, str):
            interval_ = interval
        else:
            raise TypeError('Wrong type for interval')
        await self._handle_sub_unsub(
            topic=f'market.{symbol}.kline.{interval_}',
            action=action,
        )

    async def ticker_stream(self, symbol: str, action: SubUnsub) -> None:
        if not isinstance(symbol, str):
            raise TypeError('Symbol is not str')
        await self._handle_sub_unsub(
            topic=f'market.{symbol}.ticker',
            action=action,
        )

    async def market_depth_stream(
            self,
            symbol: str,
            action: SubUnsub,
            aggregation_level: Aggregation = Aggregation.step0,
    ) -> None:
        if not isinstance(symbol, str):
            raise TypeError('Symbol is not str')
        topic = f'market.{symbol}.depth.{aggregation_level.value}'
        await self._handle_sub_unsub(
            topic=topic,
            action=action,
        )

    async def best_bid_offer_stream(self, symbol: str, action: SubUnsub) -> None:
        if not isinstance(symbol, str):
            raise TypeError('Symbol is not str')
        await self._handle_sub_unsub(
            topic=f'market.{symbol}.bbo',
            action=action,
        )

    async def trade_detail_stream(self, symbol: str, action: SubUnsub) -> None:
        if not isinstance(symbol, str):
            raise TypeError('Symbol is not str')
        await self._handle_sub_unsub(
            topic=f'market.{symbol}.trade.detail',
            action=action,
        )

    async def market_detail_stream(self, symbol: str, action: SubUnsub) -> None:
        if not isinstance(symbol, str):
            raise TypeError('Symbol is not str')
        await self._handle_sub_unsub(
            topic=f'market.{symbol}.detail',
            action=action,
        )

    async def etp_stream(self, symbol: str, action: SubUnsub) -> None:
        if not isinstance(symbol, str):
            raise TypeError('Symbol is not str')
        await self._handle_sub_unsub(
            topic=f'market.{symbol}.etp',
            action=action,
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
