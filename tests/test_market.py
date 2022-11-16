import pytest
from yarl import URL

from huobiclient.enums import CandleInterval, MarketDepth, MarketDepthAggregationLevel


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
async def test_get_candles(cfg, client, interval, size):
    await client.get_candles('btcusdt', interval, size)
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/market/history/kline'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    assert kwargs['params'] == {
        'symbol': 'btcusdt',
        'period': interval.value,
        'size': size,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [0, 2001])
async def test_get_candles_wrong_size(client, size):
    with pytest.raises(ValueError):
        await client.get_candles('btcusdt', CandleInterval.min_1, size)


@pytest.mark.asyncio
async def test_get_latest_aggregated_ticker(cfg, client):
    await client.get_latest_aggregated_ticker('btcusdt')
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/market/detail/merged'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    assert kwargs['params'] == {'symbol': 'btcusdt'}


@pytest.mark.asyncio
async def test_get_latest_tickers_for_all_pairs(cfg, client):
    await client.get_latest_tickers_for_all_pairs()
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/market/tickers'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    assert kwargs['params'] is None


@pytest.mark.asyncio
@pytest.mark.parametrize('depth', [
    MarketDepth.depth_5, MarketDepth.depth_10, MarketDepth.depth_20
])
@pytest.mark.parametrize('aggregation_level', [
    MarketDepthAggregationLevel.step0,
    MarketDepthAggregationLevel.step2
])
async def test_get_market_depth(cfg, client, depth, aggregation_level):
    await client.get_market_depth(
        symbol='btcusdt',
        depth=depth,
        aggregation_level=aggregation_level,
    )
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/market/depth'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    assert kwargs['params'] == {
        'symbol': 'btcusdt',
        'depth': depth.value,
        'type': aggregation_level.value,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [1, 2000])
async def test_get_most_recent_trades(cfg, client, size):
    await client.get_most_recent_trades(
        symbol='btcusdt',
        size=size,
    )
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/market/history/trade'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    assert kwargs['params'] == {
        'symbol': 'btcusdt',
        'size': size,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [0, 2001])
async def test_get_most_recent_trades(client, size):
    with pytest.raises(ValueError):
        await client.get_most_recent_trades(
            symbol='btcusdt',
            size=size,
        )


@pytest.mark.asyncio
async def test_get_last_market_summary(cfg, client):
    await client.get_last_market_summary(symbol='btcusdt')
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/market/detail/'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    assert kwargs['params'] == {'symbol': 'btcusdt'}


@pytest.mark.asyncio
async def test_get_real_time_nav(cfg, client):
    await client.get_real_time_nav(symbol='btcusdt')
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/market/etp/'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    assert kwargs['params'] == {'symbol': 'btcusdt'}
