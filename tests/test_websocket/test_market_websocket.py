import gzip
import json
from typing import Dict, List

import pytest

from asynchuobi.enums import CandleInterval, DepthLevel
from asynchuobi.exceptions import WSHuobiError
from asynchuobi.ws.ws_client import MarketWebsocket
from tests.test_websocket.stubs import NOT_FOUND_TOPIC, TOPICS, HuobiMarketWebsocketConnectionStub


def callback(msg: Dict):
    ...


def test_default_parameters(market_websocket):
    assert market_websocket._loads == json.loads
    assert market_websocket._decompress == gzip.decompress
    assert market_websocket._run_callbacks_in_asyncio_tasks is True
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_context_manager():
    async with MarketWebsocket() as ws:
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
    await market_websocket.candlestick('btcusdt', interval).sub(callback)
    topic = 'market.btcusdt.kline.1min'
    market_websocket._connection.send.assert_called_once_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_candlestick_unsubscribe(market_websocket):
    topic = 'market.btcusdt.kline.1min'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.candlestick('btcusdt', '1min').unsub()
    market_websocket._connection.send.assert_called_once_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_ticker_info(market_websocket):
    await market_websocket.market_ticker_info('btcusdt').sub(callback)
    topic = 'market.btcusdt.ticker'
    market_websocket._connection.send.assert_called_once_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_ticker_info_unsubscribe(market_websocket):
    topic = 'market.btcusdt.ticker'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.market_ticker_info('btcusdt').unsub()
    market_websocket._connection.send.assert_called_once_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_orderbook(market_websocket):
    level = DepthLevel.step0
    await market_websocket.orderbook('btcusdt').sub(callback)
    topic = f'market.btcusdt.depth.{level.value}'
    market_websocket._connection.send.assert_called_once_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_orderbook_unsubscribe(market_websocket):
    level = DepthLevel.step0
    topic = f'market.btcusdt.depth.{level.value}'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.orderbook('btcusdt').unsub()
    market_websocket._connection.send.assert_called_once_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_best_bid_offer(market_websocket):
    await market_websocket.best_bid_offer('btcusdt').sub(callback)
    topic = 'market.btcusdt.bbo'
    market_websocket._connection.send.assert_called_once_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_best_bid_offer_unsubscribe(market_websocket):
    topic = 'market.btcusdt.bbo'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.best_bid_offer('btcusdt').unsub()
    market_websocket._connection.send.assert_called_once_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_latest_trades(market_websocket):
    await market_websocket.latest_trades('btcusdt').sub(callback)
    topic = 'market.btcusdt.trade.detail'
    market_websocket._connection.send.assert_called_once_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_latest_trades_unsubscribe(market_websocket):
    topic = 'market.btcusdt.trade.detail'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.latest_trades('btcusdt').unsub()
    market_websocket._connection.send.assert_called_once_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_market_stats(market_websocket):
    await market_websocket.market_stats('btcusdt').sub(callback)
    topic = 'market.btcusdt.detail'
    market_websocket._connection.send.assert_called_once_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_market_stats_unsubscribe(market_websocket):
    topic = 'market.btcusdt.detail'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.market_stats('btcusdt').unsub()
    market_websocket._connection.send.assert_called_once_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_market_websocket():
    received = []
    async with MarketWebsocket(
        connection=HuobiMarketWebsocketConnectionStub,
        topics=TOPICS,
    ) as ws:
        await ws.candlestick('btcusdt', '1min').sub()
        async for message in ws:
            received.append(message)
    assert received == [
        {'status': 'ok', 'subbed': 'market.btcusdt.kline.1min', 'ts': 1},
        {'status': 'error', 'err-code': 'code', 'err-msg': 'msg', 'ts': 1},
    ]
    assert ws._connection._sent_messages == [
        {'sub': 'market.btcusdt.kline.1min'},
        {'pong': 1},
        {'pong': 2},
    ]


@pytest.mark.asyncio
async def test_market_websocket_callbacks():
    received: List[Dict] = []
    errors: List[WSHuobiError] = []

    def candle_callback(msg: Dict):
        received.append(msg)

    def error_callback(error: WSHuobiError):
        errors.append(error)

    async with MarketWebsocket(
        connection=HuobiMarketWebsocketConnectionStub,
        topics=TOPICS,
    ) as ws:
        await ws.candlestick('btcusdt', '1min').sub(candle_callback)
        await ws.run_with_callbacks(
            error_callback=error_callback,
        )
    assert received == [
        {'status': 'ok', 'subbed': 'market.btcusdt.kline.1min', 'ts': 1},
    ]
    assert len(errors) == 1
    assert errors[0].err_code == 'code'
    assert errors[0].err_msg == 'msg'


@pytest.mark.asyncio
async def test_market_websocket_not_found_topic():
    def error_callback(error: WSHuobiError):
        ...

    async with MarketWebsocket(
        connection=HuobiMarketWebsocketConnectionStub,
        topics=NOT_FOUND_TOPIC,
    ) as ws:
        with pytest.raises(ValueError) as err:
            await ws.run_with_callbacks(
                error_callback=error_callback,
            )
        assert err.value.args[0] == 'Not found topic in {}'


@pytest.mark.asyncio
async def test_market_websocket_not_specified_callback():
    def error_callback(error: WSHuobiError):
        ...

    async with MarketWebsocket(
        connection=HuobiMarketWebsocketConnectionStub,
        topics=TOPICS,
    ) as ws:
        with pytest.raises(ValueError) as err:
            await ws.run_with_callbacks(
                error_callback=error_callback,
            )
        assert err.value.args[0] == 'Not specified callback for topic "market.btcusdt.kline.1min"'


@pytest.mark.asyncio
async def test_market_websocket_error_callback_not_callable():
    async with MarketWebsocket(
        connection=HuobiMarketWebsocketConnectionStub,
    ) as ws:
        with pytest.raises(TypeError) as err:
            await ws.run_with_callbacks(
                error_callback=10,
            )
        assert err.value.args[0] == 'Callback 10 is not callable'
