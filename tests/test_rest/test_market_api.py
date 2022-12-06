from urllib.parse import urljoin

import pytest

from asynchuobi.enums import CandleInterval, MarketDepth, MarketDepthAggregationLevel
from asynchuobi.urls import HUOBI_API_URL


@pytest.mark.asyncio
@pytest.mark.parametrize('interval', [
    CandleInterval.min_1,
    CandleInterval.min_5,
    CandleInterval.min_15,
    CandleInterval.min_30,
    CandleInterval.min_60,
    CandleInterval.hour_4,
    CandleInterval.day_1,
    CandleInterval.mon_1,
    CandleInterval.week_1,
    CandleInterval.year_1,
])
@pytest.mark.parametrize('size', [1, 2000])
async def test_get_candles(market_client, interval, size):
    await market_client.get_candles('btcusdt', interval, size)
    kwargs = market_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert market_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/market/history/kline')
    assert kwargs['params'] == {
        'symbol': 'btcusdt',
        'period': interval.value,
        'size': size,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [0, 2001])
async def test_get_candles_wrong_size(market_client, size):
    with pytest.raises(ValueError):
        await market_client.get_candles('btcusdt', CandleInterval.min_1, size)


@pytest.mark.asyncio
async def test_get_latest_aggregated_ticker(market_client):
    await market_client.get_latest_aggregated_ticker('btcusdt')
    kwargs = market_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert market_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/market/detail/merged')
    assert kwargs['params'] == {'symbol': 'btcusdt'}


@pytest.mark.asyncio
async def test_get_latest_tickers_for_all_pairs(market_client):
    await market_client.get_latest_tickers_for_all_pairs()
    kwargs = market_client._requests.get.call_args.kwargs
    assert len(kwargs) == 1
    assert market_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/market/tickers')


@pytest.mark.asyncio
@pytest.mark.parametrize('depth', [
    MarketDepth.depth_5, MarketDepth.depth_10, MarketDepth.depth_20
])
@pytest.mark.parametrize('aggregation_level', [
    MarketDepthAggregationLevel.step0,
    MarketDepthAggregationLevel.step2
])
async def test_get_market_depth(market_client, depth, aggregation_level):
    await market_client.get_market_depth(
        symbol='btcusdt',
        depth=depth,
        aggregation_level=aggregation_level,
    )
    kwargs = market_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert market_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/market/depth')
    assert kwargs['params'] == {
        'symbol': 'btcusdt',
        'depth': depth.value,
        'type': aggregation_level.value,
    }


@pytest.mark.asyncio
async def test_get_last_trade(market_client):
    await market_client.get_last_trade(
        symbol='btcusdt'
    )
    kwargs = market_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert market_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/market/trade')
    assert kwargs['params'] == {
        'symbol': 'btcusdt',
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [1, 2000])
async def test_get_most_recent_trades(market_client, size):
    await market_client.get_most_recent_trades(
        symbol='btcusdt',
        size=size,
    )
    kwargs = market_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert market_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/market/history/trade')
    assert kwargs['params'] == {
        'symbol': 'btcusdt',
        'size': size,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [0, 2001])
async def test_get_most_recent_trades_wrong_size(market_client, size):
    with pytest.raises(ValueError):
        await market_client.get_most_recent_trades(
            symbol='btcusdt',
            size=size,
        )


@pytest.mark.asyncio
async def test_get_last_market_summary(market_client):
    await market_client.get_last_market_summary(symbol='btcusdt')
    kwargs = market_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert market_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/market/detail/')
    assert kwargs['params'] == {'symbol': 'btcusdt'}


@pytest.mark.asyncio
async def test_get_real_time_nav(market_client):
    await market_client.get_real_time_nav(symbol='btcusdt')
    kwargs = market_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert market_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/market/etp/')
    assert kwargs['params'] == {'symbol': 'btcusdt'}
