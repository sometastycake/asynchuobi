from urllib.parse import urljoin

import pytest

from huobiclient.cfg import HUOBI_API_URL


@pytest.mark.asyncio
async def test_get_system_status(generic_client):
    await generic_client.get_system_status()
    kwargs = generic_client._rstrategy.request.call_args.kwargs
    assert kwargs['url'] == 'https://status.huobigroup.com/api/v2/summary.json'
    assert kwargs['method'] == 'GET'
    assert kwargs['headers'] == {'Content-Type': 'application/json'}
    assert len(kwargs) == 3


@pytest.mark.asyncio
async def test_get_market_status(generic_client):
    await generic_client.get_market_status()
    kwargs = generic_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 2
    assert generic_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/market-status')
    assert kwargs['method'] == 'GET'


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
async def test_get_all_supported_trading_symbols(generic_client, timestamp):
    await generic_client.get_all_supported_trading_symbols(
        timestamp_milliseconds=timestamp,
    )
    kwargs = generic_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert generic_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/settings/common/symbols')
    assert kwargs['method'] == 'GET'
    if timestamp is None:
        assert kwargs['params'] == {}
    else:
        assert kwargs['params'] == {'ts': timestamp}


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
async def test_get_all_supported_currencies(generic_client, timestamp):
    await generic_client.get_all_supported_currencies(
        timestamp_milliseconds=timestamp,
    )
    kwargs = generic_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert generic_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/settings/common/currencies')
    assert kwargs['method'] == 'GET'
    if timestamp is None:
        assert kwargs['params'] == {}
    else:
        assert kwargs['params'] == {'ts': timestamp}


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
async def test_get_currencies_settings(generic_client, timestamp):
    await generic_client.get_currencies_settings(
        timestamp_milliseconds=timestamp,
    )
    kwargs = generic_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert generic_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/settings/common/currencys')
    assert kwargs['method'] == 'GET'
    if timestamp is None:
        assert kwargs['params'] == {}
    else:
        assert kwargs['params'] == {'ts': timestamp}


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
async def test_get_symbols_settings(generic_client, timestamp):
    await generic_client.get_symbols_settings(
        timestamp_milliseconds=timestamp,
    )
    kwargs = generic_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert generic_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/settings/common/symbols')
    assert kwargs['method'] == 'GET'
    if timestamp is None:
        assert kwargs['params'] == {}
    else:
        assert kwargs['params'] == {'ts': timestamp}


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
@pytest.mark.parametrize('symbols', [None, ('btcusdt', ), {'btcusdt', 'ethusdt'}])
async def test_get_market_symbols_settings(generic_client, timestamp, symbols):
    await generic_client.get_market_symbols_settings(
        symbols=symbols,
        timestamp_milliseconds=timestamp,
    )
    kwargs = generic_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert generic_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/settings/common/market-symbols')
    assert kwargs['method'] == 'GET'
    request = {}
    if timestamp is not None:
        request['ts'] = timestamp
    if symbols is not None:
        request['symbols'] = ','.join(symbols)
    assert kwargs['params'] == request


@pytest.mark.asyncio
@pytest.mark.parametrize('symbols', [1, False])
async def test_get_market_symbols_settings_wrong_symbols(generic_client, symbols):
    with pytest.raises(TypeError):
        await generic_client.get_market_symbols_settings(
            symbols=symbols,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('timestamp', [None, 1])
@pytest.mark.parametrize('show_desc', [None, 0, 1, 2])
@pytest.mark.parametrize('currency', [None, 'btc'])
async def test_get_chains_information(generic_client, timestamp, show_desc, currency):
    await generic_client.get_chains_information(
        show_desc=show_desc,
        timestamp_milliseconds=timestamp,
        currency=currency,
    )
    kwargs = generic_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert generic_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/settings/common/chains')
    assert kwargs['method'] == 'GET'
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
async def test_get_chains_information_v2(generic_client, currency, authorized_user):
    await generic_client.get_chains_information_v2(
        currency=currency,
        authorized_user=authorized_user,
    )
    kwargs = generic_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert generic_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/reference/currencies')
    assert kwargs['method'] == 'GET'
    params = {
        'authorizedUser': str(authorized_user).lower(),
    }
    if currency is not None:
        params['currency'] = currency
    assert kwargs['params'] == params


@pytest.mark.asyncio
async def test_get_current_timestamp(generic_client):
    await generic_client.get_current_timestamp()
    kwargs = generic_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 2
    assert generic_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, 'v1/common/timestamp')
    assert kwargs['method'] == 'GET'
