import gzip
import json
from typing import Dict, List

import pytest

from asynchuobi.enums import CandleInterval, DepthLevel
from asynchuobi.exceptions import WSHuobiError
from asynchuobi.ws.ws_client import _base_stream  # noqa
from asynchuobi.ws.ws_client import _best_bid_offer  # noqa
from asynchuobi.ws.ws_client import _candles  # noqa
from asynchuobi.ws.ws_client import _latest_trades  # noqa
from asynchuobi.ws.ws_client import _market_stats  # noqa
from asynchuobi.ws.ws_client import _market_ticker_info  # noqa
from asynchuobi.ws.ws_client import _orderbook  # noqa
from asynchuobi.ws.ws_client import WSHuobiMarket
from tests.test_websocket.stubs.ws_market_stub import (
    WS_MARKET_MESSAGES,
    WS_MARKET_MESSAGES_WITHOUT_TOPIC,
    WSHuobiMarketConnectionStub,
)


def _callback(msg: Dict):
    ...


def test_candles_topic(market_websocket):
    stream = _candles(market_websocket, 'btcusdt', '1min')
    assert stream.topic == 'market.btcusdt.kline.1min'


def test_market_ticker_info_topic(market_websocket):
    stream = _market_ticker_info(market_websocket, 'btcusdt')
    assert stream.topic == 'market.btcusdt.ticker'


def test_orderbook_topic(market_websocket):
    stream = _orderbook(market_websocket, 'btcusdt', DepthLevel.step0)
    assert stream.topic == 'market.btcusdt.depth.step0'


def test_best_bid_offer_topic(market_websocket):
    stream = _best_bid_offer(market_websocket, 'btcusdt')
    assert stream.topic == 'market.btcusdt.bbo'


def test_latest_trades_topic(market_websocket):
    stream = _latest_trades(market_websocket, 'btcusdt')
    assert stream.topic == 'market.btcusdt.trade.detail'


def test_market_stats_topic(market_websocket):
    stream = _market_stats(market_websocket, 'btcusdt')
    assert stream.topic == 'market.btcusdt.detail'


def test_base_stream_wrong_symbol(market_websocket):
    with pytest.raises(TypeError):
        _base_stream(market_websocket, 10)  # type:ignore


def test_default_parameters(market_websocket):
    assert market_websocket._loads == json.loads
    assert market_websocket._decompress == gzip.decompress
    assert market_websocket._run_callbacks_in_asyncio_tasks is False
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_context_manager():
    async with WSHuobiMarket() as ws:
        assert ws._connection.closed is False


@pytest.mark.asyncio
async def test_pong(market_websocket):
    await market_websocket._pong(1)
    market_websocket._connection.send.assert_called_once_with({'pong': 1})


@pytest.mark.asyncio
async def test_close(market_websocket, monkeypatch):
    monkeypatch.setattr(market_websocket._connection, 'closed', False)
    await market_websocket.close()
    market_websocket._connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_handler_wrong_callback(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket.send_message_handler(
            topic='topic',
            action='sub',
            callback='callback',
        )


@pytest.mark.asyncio
async def test_candlestick_wrong_interval(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket.candlestick(
            symbol='btcusdt',
            interval=10,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('interval', [CandleInterval.min_1, '1min'])
async def test_candlestick(market_websocket, interval):
    topic = 'market.btcusdt.kline.1min'
    # Subscribe
    await market_websocket.candlestick('btcusdt', interval).sub(_callback)
    market_websocket._connection.send.assert_called_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == _callback
    # Unsubscribe
    await market_websocket.candlestick('btcusdt', interval).unsub()
    market_websocket._connection.send.assert_called_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_ticker_info(market_websocket):
    topic = 'market.btcusdt.ticker'
    # Subscribe
    await market_websocket.market_ticker_info('btcusdt').sub(_callback)
    market_websocket._connection.send.assert_called_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == _callback
    # Unsubscribe
    await market_websocket.market_ticker_info('btcusdt').unsub()
    market_websocket._connection.send.assert_called_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_orderbook(market_websocket):
    level = DepthLevel.step0
    topic = f'market.btcusdt.depth.{level.value}'
    # Subscribe
    await market_websocket.orderbook('btcusdt').sub(_callback)
    market_websocket._connection.send.assert_called_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == _callback
    # Unsubscribe
    await market_websocket.orderbook('btcusdt').unsub()
    market_websocket._connection.send.assert_called_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_best_bid_offer(market_websocket):
    topic = 'market.btcusdt.bbo'
    # Subscribe
    await market_websocket.best_bid_offer('btcusdt').sub(_callback)
    market_websocket._connection.send.assert_called_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == _callback
    # Unsubscribe
    await market_websocket.best_bid_offer('btcusdt').unsub()
    market_websocket._connection.send.assert_called_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_latest_trades(market_websocket):
    topic = 'market.btcusdt.trade.detail'
    # Subscribe
    await market_websocket.latest_trades('btcusdt').sub(_callback)
    market_websocket._connection.send.assert_called_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == _callback
    # Unsubscribe
    await market_websocket.latest_trades('btcusdt').unsub()
    market_websocket._connection.send.assert_called_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_market_stats(market_websocket):
    topic = 'market.btcusdt.detail'
    # Subscribe
    await market_websocket.market_stats('btcusdt').sub(_callback)
    market_websocket._connection.send.assert_called_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == _callback
    # Unsubscribe
    await market_websocket.market_stats('btcusdt').unsub()
    market_websocket._connection.send.assert_called_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_market_websocket_iteration():
    received = []
    topic = 'market.btcusdt.kline.1min'
    async with WSHuobiMarket(
        connection=WSHuobiMarketConnectionStub,
        topics=WS_MARKET_MESSAGES,
    ) as ws:
        await ws.candlestick('btcusdt', '1min').sub()
        async for message in ws:
            received.append(message)
    assert ws._connection._sent_messages == [
        {'sub': topic}, {'pong': 1}, {'pong': 2},
    ]
    assert received == [
        {
            'status': 'ok',
            'subbed': topic,
            'ts': 1,
        },
        {
            'ch': topic,
            'ts': 1,
            'tick': {
                'open': 1,
            }
        },
        {
            'status': 'ok',
            'unsubbed': topic,
            'ts': 1,
        },
        {
            'status': 'error',
            'err-code': 'code',
            'err-msg': 'msg',
            'ts': 1,
        },
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize('is_async_call', [True, False])
async def test_market_websocket_callbacks(is_async_call):
    if is_async_call:
        class Callback:
            received = []

            async def __call__(self, message: Dict):
                self.received.append(message)
    else:
        class Callback:
            received = []

            def __call__(self, message: Dict):
                self.received.append(message)

    if is_async_call:
        class Error:
            errors = []

            async def __call__(self, error: WSHuobiError):
                self.errors.append(error)
    else:
        class Error:
            errors = []

            def __call__(self, error: WSHuobiError):
                self.errors.append(error)

    async with WSHuobiMarket(
        connection=WSHuobiMarketConnectionStub,
        run_callbacks_in_asyncio_tasks=False,
        topics=WS_MARKET_MESSAGES,
    ) as ws:
        await ws.candlestick('btcusdt', '1min').sub(Callback())
        await ws.run_with_callbacks(Error())
    assert Callback.received == [
        {
            'status': 'ok',
            'subbed': 'market.btcusdt.kline.1min',
            'ts': 1,
        },
        {
            'ch': 'market.btcusdt.kline.1min',
            'ts': 1,
            'tick': {
                'open': 1,
            },
        },
        {
            'status': 'ok',
            'unsubbed': 'market.btcusdt.kline.1min',
            'ts': 1,
        },
    ]
    assert len(Error.errors) == 1
    assert Error.errors[0].err_code == 'code'
    assert Error.errors[0].err_msg == 'msg'


@pytest.mark.asyncio
@pytest.mark.parametrize('is_async_call', [True, False])
async def test_market_websocket_simple_callbacks(is_async_call):
    received: List[Dict] = []
    errors: List[WSHuobiError] = []

    if is_async_call:
        async def callback(message: Dict):
            received.append(message)

        async def error(e: WSHuobiError):
            errors.append(e)
    else:
        def callback(message: Dict):
            received.append(message)

        def error(e: WSHuobiError):
            errors.append(e)

    ws = WSHuobiMarket(
        connection=WSHuobiMarketConnectionStub,
        run_callbacks_in_asyncio_tasks=False,
        topics=WS_MARKET_MESSAGES,
    )
    await ws.candlestick('btcusdt', '1min').sub(callback)
    await ws.run_with_callbacks(error)
    assert received == [
        {
            'status': 'ok',
            'subbed': 'market.btcusdt.kline.1min',
            'ts': 1,
        },
        {
            'ch': 'market.btcusdt.kline.1min',
            'ts': 1,
            'tick': {
                'open': 1,
            },
        },
        {
            'status': 'ok',
            'unsubbed': 'market.btcusdt.kline.1min',
            'ts': 1,
        },
    ]
    assert len(errors) == 1
    assert errors[0].err_code == 'code'
    assert errors[0].err_msg == 'msg'


@pytest.mark.asyncio
async def test_market_websocket_not_found_topic():
    async def error_callback(error: WSHuobiError):
        ...

    async with WSHuobiMarket(
        connection=WSHuobiMarketConnectionStub,
        topics=WS_MARKET_MESSAGES_WITHOUT_TOPIC,
    ) as ws:
        with pytest.raises(ValueError) as err:
            await ws.run_with_callbacks(
                error_callback=error_callback,
            )
        assert err.value.args[0] == 'Not found topic in {}'


@pytest.mark.asyncio
async def test_market_websocket_not_specified_callback():
    async def error_callback(error: WSHuobiError):
        ...

    async with WSHuobiMarket(
        connection=WSHuobiMarketConnectionStub,
        topics=WS_MARKET_MESSAGES,
    ) as ws:
        with pytest.raises(ValueError) as err:
            await ws.run_with_callbacks(
                error_callback=error_callback,
            )
        assert err.value.args[0] == 'Not specified callback for topic "market.btcusdt.kline.1min"'


@pytest.mark.asyncio
async def test_market_websocket_error_callback_not_callable():
    async with WSHuobiMarket(
        connection=WSHuobiMarketConnectionStub,
    ) as ws:
        with pytest.raises(TypeError) as err:
            await ws.run_with_callbacks(
                error_callback=10,
            )
        assert err.value.args[0] == 'Callback 10 is not callable'
