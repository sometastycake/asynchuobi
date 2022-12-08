import gzip
import json
from typing import Dict

import pytest

from asynchuobi.enums import CandleInterval, MarketDepthAggregationLevel
from asynchuobi.ws.enums import Subcription
from asynchuobi.ws.ws_client import HuobiMarketWebsocket, _default_message_id  # noqa


def callback(msg: Dict):
    ...


async def async_callback(msg: Dict):
    ...


def test_default_parameters(market_websocket):
    assert market_websocket._loads == json.loads
    assert market_websocket._decompress == gzip.decompress
    assert market_websocket._default_message_id == _default_message_id
    assert market_websocket._raise_if_error is False
    assert market_websocket._run_callbacks_in_asyncio_tasks is True
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_context_manager():
    async with HuobiMarketWebsocket() as ws:
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
async def test_unsubscribe_all(market_websocket, monkeypatch):
    monkeypatch.setattr(market_websocket, '_subscribed_ch', ['topic1', 'topic2'])
    monkeypatch.setattr(market_websocket._connection, 'closed', False)
    await market_websocket.unsubscribe_all()
    assert market_websocket._subscribed_ch == []
    assert len(market_websocket._connection.method_calls) == 2
    for call, topic in zip(market_websocket._connection.method_calls, ('topic1', 'topic2')):
        assert call.args[0] == {'unsub': topic}


@pytest.mark.asyncio
async def test_unsubscribe_all_with_closed_connection(market_websocket, monkeypatch):
    monkeypatch.setattr(market_websocket._connection, 'closed', True)
    await market_websocket.unsubscribe_all()
    assert market_websocket._connection.call_count == 0
    assert market_websocket._connection.await_count == 0


@pytest.mark.asyncio
async def test_handler_wrong_action(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket._handler('topic', 'action')


@pytest.mark.asyncio
async def test_handler_wrong_callback(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket._handler(
            topic='topic',
            action=Subcription.sub,
            callback='callback',
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('message_id', [None, 'id'])
@pytest.mark.parametrize('topic', ['topic1', 'topic2'])
async def test_handler_subscribe(market_websocket, message_id, topic):
    await market_websocket._handler(
        topic=topic,
        action=Subcription.sub,
        message_id=message_id,
    )
    message = {Subcription.sub.value: topic}
    if message_id is not None:
        message['id'] = message_id
    market_websocket._connection.send.assert_called_once_with(message)
    assert topic in market_websocket._subscribed_ch


@pytest.mark.asyncio
async def test_handler_unsubscribe(market_websocket, monkeypatch):
    monkeypatch.setattr(market_websocket, '_subscribed_ch', {'topic'})
    await market_websocket._handler(
        topic='topic',
        action=Subcription.unsub,
    )
    message = {Subcription.unsub.value: 'topic'}
    market_websocket._connection.send.assert_called_once_with(message)
    assert market_websocket._subscribed_ch == set()


@pytest.mark.asyncio
async def test_market_candlestick_stream_wrong_symbol(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket.candlestick(
            symbol=10,
            action=Subcription.sub,
        )


@pytest.mark.asyncio
async def test_market_candlestick_stream_wrong_interval(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket.candlestick(
            symbol='btcusdt',
            action=Subcription.sub,
            interval=10,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('interval', [CandleInterval.min_1, '1min'])
async def test_market_candlestick_stream(market_websocket, interval):
    await market_websocket.candlestick(
        symbol='btcusdt',
        interval=interval,
        action=Subcription.sub,
        message_id='id',
        callback=callback,
    )
    topic = 'market.btcusdt.kline.1min'
    market_websocket._connection.send.assert_called_once_with({
        'sub': topic,
        'id': 'id',
    })
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_market_candlestick_stream_unsubscribe(market_websocket):
    topic = 'market.btcusdt.kline.1min'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.candlestick(
        symbol='btcusdt',
        interval='1min',
        action=Subcription.unsub,
        message_id='id',
        callback=async_callback,
    )
    market_websocket._connection.send.assert_called_once_with({
        'unsub': topic,
        'id': 'id',
    })
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_ticker_stream_wrong_symbol(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket.ticker_info(10, Subcription.sub)


@pytest.mark.asyncio
async def test_ticker_stream(market_websocket):
    await market_websocket.ticker_info(
        symbol='btcusdt',
        action=Subcription.sub,
        callback=callback,
    )
    market_websocket._connection.send.assert_called_once_with({'sub': 'market.btcusdt.ticker'})
    assert market_websocket._subscribed_ch == {'market.btcusdt.ticker'}
    assert market_websocket._callbacks['market.btcusdt.ticker'] == callback


@pytest.mark.asyncio
async def test_ticker_stream_unsubscribe(market_websocket):
    market_websocket._subscribed_ch = {'market.btcusdt.ticker'}
    market_websocket._callbacks['market.btcusdt.ticker'] = callback
    await market_websocket.ticker_info(
        symbol='btcusdt',
        action=Subcription.unsub,
        callback=async_callback,
    )
    market_websocket._connection.send.assert_called_once_with({'unsub': 'market.btcusdt.ticker'})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_market_depth_stream_wrong_symbol(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket.orderbook(
            symbol=10,
            action=Subcription.sub,
        )


@pytest.mark.asyncio
async def test_market_depth_stream(market_websocket):
    level = MarketDepthAggregationLevel.step0
    await market_websocket.orderbook(
        symbol='btcusdt',
        action=Subcription.sub,
        callback=callback,
        level=level,
        message_id='id',
    )
    topic = f'market.btcusdt.depth.{level.value}'
    market_websocket._connection.send.assert_called_once_with({'sub': topic, 'id': 'id'})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_market_depth_stream_unsubscribe(market_websocket):
    level = MarketDepthAggregationLevel.step0
    topic = f'market.btcusdt.depth.{level.value}'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.orderbook(
        symbol='btcusdt',
        action=Subcription.unsub,
        callback=async_callback,
        level=level,
        message_id='id',
    )
    market_websocket._connection.send.assert_called_once_with({'unsub': topic, 'id': 'id'})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_best_bid_offer_stream_wrong_symbol(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket.best_bid_offer(
            symbol=10,
            action=Subcription.sub,
        )


@pytest.mark.asyncio
async def test_best_bid_offer_stream(market_websocket):
    await market_websocket.best_bid_offer(
        symbol='btcusdt',
        action=Subcription.sub,
        callback=callback,
        message_id='id',
    )
    topic = 'market.btcusdt.bbo'
    market_websocket._connection.send.assert_called_once_with({'sub': topic, 'id': 'id'})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_best_bid_offer_stream_unsubscribe(market_websocket):
    topic = 'market.btcusdt.bbo'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.best_bid_offer(
        symbol='btcusdt',
        action=Subcription.unsub,
        callback=async_callback,
        message_id='id',
    )
    market_websocket._connection.send.assert_called_once_with({'unsub': topic, 'id': 'id'})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_trade_detail_stream_wrong_symbol(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket.trade_detail(
            symbol=10,
            action=Subcription.sub,
        )


@pytest.mark.asyncio
async def test_trade_detail_stream(market_websocket):
    await market_websocket.trade_detail(
        symbol='btcusdt',
        action=Subcription.sub,
        callback=callback,
        message_id='id',
    )
    topic = 'market.btcusdt.trade.detail'
    market_websocket._connection.send.assert_called_once_with({'sub': topic, 'id': 'id'})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_trade_detail_stream_unsubscribe(market_websocket):
    topic = 'market.btcusdt.trade.detail'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.trade_detail(
        symbol='btcusdt',
        action=Subcription.unsub,
        callback=async_callback,
        message_id='id',
    )
    market_websocket._connection.send.assert_called_once_with({'unsub': topic, 'id': 'id'})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_market_detail_stream_wrong_symbol(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket.market_detail(
            symbol=10,
            action=Subcription.sub,
        )


@pytest.mark.asyncio
async def test_market_detail_stream(market_websocket):
    await market_websocket.market_detail(
        symbol='btcusdt',
        action=Subcription.sub,
        callback=callback,
        message_id='id',
    )
    topic = 'market.btcusdt.detail'
    market_websocket._connection.send.assert_called_once_with({'sub': topic, 'id': 'id'})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_market_detail_stream_unsubscribe(market_websocket):
    topic = 'market.btcusdt.detail'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.market_detail(
        symbol='btcusdt',
        action=Subcription.unsub,
        callback=async_callback,
        message_id='id',
    )
    market_websocket._connection.send.assert_called_once_with({'unsub': topic, 'id': 'id'})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_etp_stream_wrong_symbol(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket.etp(
            symbol=10,
            action=Subcription.sub,
        )


@pytest.mark.asyncio
async def test_etp_stream(market_websocket):
    await market_websocket.etp(
        symbol='btcusdt',
        action=Subcription.sub,
        callback=callback,
    )
    topic = 'market.btcusdt.etp'
    market_websocket._connection.send.assert_called_once_with({'sub': topic})
    assert market_websocket._subscribed_ch == {topic}
    assert market_websocket._callbacks[topic] == callback


@pytest.mark.asyncio
async def test_etp_stream_unsubscribe(market_websocket):
    topic = 'market.btcusdt.etp'
    market_websocket._subscribed_ch = {topic}
    market_websocket._callbacks[topic] = callback
    await market_websocket.etp(
        symbol='btcusdt',
        action=Subcription.unsub,
        callback=async_callback,
    )
    market_websocket._connection.send.assert_called_once_with({'unsub': topic})
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}
