import pytest
from yarl import URL


@pytest.mark.asyncio
async def test_get_system_status(client):
    await client.get_system_status()
    kwargs = client._session.get.call_args.kwargs
    assert kwargs['url'] == 'https://status.huobigroup.com/api/v2/summary.json'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert len(kwargs) == 2


@pytest.mark.asyncio
async def test_get_market_status(cfg, client):
    await client.get_market_status()
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/v2/market-status'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    assert kwargs['params'] is None


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
async def test_get_all_supported_trading_symbols(cfg, client, timestamp):
    await client.get_all_supported_trading_symbols(
        timestamp_milliseconds=timestamp,
    )
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/v2/settings/common/symbols'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    if timestamp is None:
        assert kwargs['params'] == {}
    else:
        assert kwargs['params'] == {'ts': timestamp}


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
async def test_get_all_supported_currencies(cfg, client, timestamp):
    await client.get_all_supported_currencies(
        timestamp_milliseconds=timestamp,
    )
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/v2/settings/common/currencies'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    if timestamp is None:
        assert kwargs['params'] == {}
    else:
        assert kwargs['params'] == {'ts': timestamp}


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
async def test_get_currencies_settings(cfg, client, timestamp):
    await client.get_currencies_settings(
        timestamp_milliseconds=timestamp,
    )
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/v1/settings/common/currencys'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    if timestamp is None:
        assert kwargs['params'] == {}
    else:
        assert kwargs['params'] == {'ts': timestamp}


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
async def test_get_symbols_settings(cfg, client, timestamp):
    await client.get_symbols_settings(
        timestamp_milliseconds=timestamp,
    )
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/v1/settings/common/symbols'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    if timestamp is None:
        assert kwargs['params'] == {}
    else:
        assert kwargs['params'] == {'ts': timestamp}


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
@pytest.mark.parametrize('symbols', [None, ('btcusdt', ), {'btcusdt', 'ethusdt'}])
async def test_get_market_symbols_settings(cfg, client, timestamp, symbols):
    await client.get_market_symbols_settings(
        symbols=symbols,
        timestamp_milliseconds=timestamp,
    )
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/v1/settings/common/market-symbols'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    request = {}
    if timestamp is not None:
        request['ts'] = timestamp
    if symbols is not None:
        request['symbols'] = ','.join(symbols)
    assert kwargs['params'] == request


@pytest.mark.asyncio
@pytest.mark.parametrize('symbols', [1, False])
async def test_get_market_symbols_settings_wrong_symbols(client, symbols):
    with pytest.raises(TypeError):
        await client.get_market_symbols_settings(
            symbols=symbols,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
@pytest.mark.parametrize('show_desc', [None, 0, 1, 2])
@pytest.mark.parametrize('currency', [None, 'btc'])
async def test_get_chains_information(cfg, client, timestamp, show_desc, currency):
    await client.get_chains_information(
        show_desc=show_desc,
        timestamp_milliseconds=timestamp,
        currency=currency,
    )
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/v1/settings/common/chains'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    request = {}
    if show_desc is not None:
        request['show-desc'] = show_desc
    if timestamp is not None:
        request['ts'] = timestamp
    if currency is not None:
        request['currency'] = currency
    assert kwargs['params'] == request


@pytest.mark.asyncio
@pytest.mark.parametrize('currency', [None, 'btc'])
@pytest.mark.parametrize('authorized_user', [False, True])
async def test_get_chains_information_v2(cfg, client, currency, authorized_user):
    await client.get_chains_information_v2(
        currency=currency,
        authorized_user=authorized_user,
    )
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('/v2/reference/currencies'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    params = {
        'authorizedUser': str(authorized_user).lower(),
    }
    if currency is not None:
        params['currency'] = currency
    assert kwargs['params'] == params


@pytest.mark.asyncio
async def test_get_current_timestamp(cfg, client):
    await client.get_current_timestamp()
    kwargs = client._session.request.call_args.kwargs
    assert len(kwargs) == 6
    assert client._session.request.call_count == 1
    assert kwargs['url'] == str(URL(cfg.HUOBI_API_URL).with_path('v1/common/timestamp'))
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert kwargs['data'] is None
    assert kwargs['json'] is None
    assert kwargs['params'] is None
