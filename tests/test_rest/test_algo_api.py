from datetime import datetime
from urllib.parse import urljoin

import pytest
from freezegun import freeze_time

from asynchuobi.api.clients.algo import AlgoHuobiClient
from asynchuobi.enums import ConditionalOrderType, OrderSide, Sort
from asynchuobi.urls import HUOBI_API_URL
from tests.keys import HUOBI_ACCESS_KEY


@pytest.mark.asyncio
@pytest.mark.parametrize('access_key, secret_key', [('key', ''), ('', 'key')])
async def test_algo_api_wrong_keys(access_key, secret_key):
    with pytest.raises(ValueError):
        AlgoHuobiClient(access_key=access_key, secret_key=secret_key)


@pytest.mark.asyncio
@pytest.mark.parametrize('order_price', [None, 1.0])
@pytest.mark.parametrize('order_side', [OrderSide.buy, OrderSide.sell])
@pytest.mark.parametrize('order_size', [None, 2.0])
@pytest.mark.parametrize('order_value', [None, 3.0])
@pytest.mark.parametrize('time_in_force', [None, '4'])
@pytest.mark.parametrize('order_type', [
    ConditionalOrderType.limit, ConditionalOrderType.market,
])
@pytest.mark.parametrize('trailing_rate', [None, 5.0])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_new_conditional_order(
        algo_client, order_price, order_side, order_size,
        order_value, time_in_force, order_type, trailing_rate,
):
    await algo_client.new_conditional_order(
        account_id=10,
        symbol='btcusdt',
        order_price=order_price,
        order_side=order_side,
        order_size=order_size,
        order_type=order_type,
        order_value=order_value,
        time_in_force=time_in_force,
        trailing_rate=trailing_rate,
        client_order_id='client-order-id',
        stop_price=20,
    )
    kwargs = algo_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert algo_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/algo-orders')
    assert kwargs['params'] == {
        'Signature': '9V5wlubOheYTK4g+NzHNYkYJTymktU7lZBkgyOQ3zVc=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }
    data = {
        'accountId': 10,
        'symbol': 'btcusdt',
        'orderSide': order_side.value,
        'orderType': order_type.value,
        'clientOrderId': 'client-order-id',
        'stopPrice': 20.0,
    }
    if order_price is not None:
        data['orderPrice'] = order_price
    if order_size is not None:
        data['orderSize'] = order_size
    if order_value is not None:
        data['orderValue'] = order_value
    if time_in_force is not None:
        data['timeInForce'] = time_in_force
    if trailing_rate is not None:
        data['trailingRate'] = trailing_rate
    assert kwargs['json'] == data


@pytest.mark.asyncio
async def test_cancel_conditional_orders_wrong_client_order_ids(algo_client):
    with pytest.raises(TypeError):
        await algo_client.cancel_conditional_orders(1)


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_cancel_conditional_orders(algo_client):
    await algo_client.cancel_conditional_orders(
        client_order_ids=['a', 'b'],
    )
    kwargs = algo_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert algo_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/algo-orders/cancellation')
    assert kwargs['params'] == {
        'Signature': 'NO6/TJuI3wSuhpYckwW+H3tO2hglX8ylftvswRyoYgo=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }
    assert kwargs['json'] == {'clientOrderIds': ['a', 'b']}


@pytest.mark.asyncio
@pytest.mark.parametrize('limit', [0, 501])
async def test_query_open_conditional_orders_wrong_limit(algo_client, limit):
    with pytest.raises(ValueError):
        await algo_client.query_open_conditional_orders(
            limit=limit,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'account_id, symbol, order_side, order_type, sorting, from_id, signature', [
        (None, None, None, None, Sort.asc, None, 'WBuxjqp9gEiTXM5RhF/wEuPln8uwV2SdLxuBc4Dmtfk='),
        (1, None, None, None, Sort.asc, None, 'HarcjdwWobOSOUOBXNEDHMh3Wz3pP1p6kZ60b3oI1Xo='),
        (1, 'btcusdt', OrderSide.buy, None, Sort.desc, None, 'Dd8IaCNY5HFCtg5RbwuNKeHIFZlGd8I5N/jh8LHYP1Q='),
        (None, None, None, ConditionalOrderType.market, Sort.desc, None,
         'HmshGk3CyN33gsuEkhaKSmD+VB/0lNb6lWGUz6RAgCk='),
        (1, None, None, ConditionalOrderType.market, Sort.desc, None,
         'VRCigwGTeLfEe9otk4tcysIplZ7xGEbIriz4SKb+JH0='),
        (None, 'btcusdt', None, ConditionalOrderType.market, Sort.desc, None,
         'zfwLslsv/daqIPUQEIEPZru98qPYv8jfK/BftVGOrLE='),
        (1, 'btcusdt', OrderSide.buy, ConditionalOrderType.limit, Sort.desc, 2,
         'TdD96IY3DVaB2nfQ9a8rvkADxOCqcE1XVruPyaYKExo='),
        (1, 'btcusdt', None, ConditionalOrderType.limit, Sort.desc, 2,
         'eNT161XlLOxM8YWFXz8MfNN0S9WSyY/DU6DfxkO1Yuw=')
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_query_open_conditional_orders(
        algo_client, account_id, symbol, order_side, order_type, sorting, from_id, signature,
):
    await algo_client.query_open_conditional_orders(
        account_id=account_id,
        symbol=symbol,
        order_side=order_side,
        order_type=order_type,
        sorting=sorting,
        from_id=from_id,
    )
    kwargs = algo_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert algo_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/algo-orders/opening')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'limit': 100,
        'sort': sorting.value,
    }
    if account_id is not None:
        params['accountId'] = account_id
    if symbol is not None:
        params['symbol'] = symbol
    if order_type is not None:
        params['orderType'] = order_type.value
    if order_side is not None:
        params['orderSide'] = order_side.value
    if from_id is not None:
        params['fromId'] = from_id
    assert kwargs['params'] == params


@pytest.mark.asyncio
async def test_query_conditional_order_history_wrong_order_status(algo_client):
    with pytest.raises(ValueError):
        await algo_client.query_conditional_order_history(
            symbol='btcusdt',
            order_status='status',
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('limit', [0, 501])
async def test_query_conditional_order_history_wrong_limit(algo_client, limit):
    with pytest.raises(ValueError):
        await algo_client.query_conditional_order_history(
            symbol='btcusdt',
            order_status='canceled',
            limit=limit,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'account_id, order_side, order_type, start_time, end_time, sorting, from_id, signature', [
        (None, None, None, None, None, Sort.asc, None, 'OAHEA/NAa7L6O48myPCVDbQMcnPjDDuIF0w2vkgsAfo='),
        (1, None, None, None, None, Sort.asc, None, '18E0Yti58mzNWkpNbGu5q+aGsxLIGLyTv/wiuweoK1k='),
        (1, OrderSide.sell, None, None, None, Sort.asc, None, '1sepCyT16FIgrM5ZFpp7ZLhaufkdchfZKZFME9iyU/s='),
        (None, None, ConditionalOrderType.market, None, None, Sort.asc, None,
         'xVnLqtCJoxfDMqMNWJw4vr0jeyNfmgb+jbMdWb1y7m8='),
        (1, OrderSide.sell, ConditionalOrderType.market, None, None, Sort.asc, None,
         'HT0DgtXKGpjX3OxiQJ5TZtBth0NulWWDtWKZ4MedlCk='),
        (None, None, None, 10, 20, Sort.asc, None, 'YBsnxQS1DZcSwCJVD+l2xfC3dEg/jBsW3geHiycjN84='),
        (None, OrderSide.sell, None, 10, 20, Sort.asc, None, 'l7ffT9NFJoP72Eus6RwXGAimxxg2GUlg0ms115rZ++A='),
        (1, OrderSide.buy, ConditionalOrderType.limit, 10, 20, Sort.desc, 5,
         'Bg4a33Zuq5cd49ajN1cjUB+i7lF1qKF0++2SoY/ocD8=')
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_query_conditional_order_history(
        algo_client, account_id, order_side, order_type, start_time, end_time, sorting, from_id, signature,
):
    await algo_client.query_conditional_order_history(
        symbol='btcusdt',
        order_status='canceled',
        account_id=account_id,
        order_side=order_side,
        order_type=order_type,
        start_time=start_time,
        end_time=end_time,
        sorting=sorting,
        from_id=from_id,
    )
    kwargs = algo_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert algo_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/algo-orders/history')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'symbol': 'btcusdt',
        'orderStatus': 'canceled',
        'limit': 100,
        'sort': sorting.value,
    }
    if account_id is not None:
        params['accountId'] = account_id
    if order_side is not None:
        params['orderSide'] = order_side.value
    if order_type is not None:
        params['orderType'] = order_type.value
    if from_id is not None:
        params['fromId'] = from_id
    if start_time is not None:
        params['startTime'] = start_time
    if end_time is not None:
        params['endTime'] = end_time
    assert kwargs['params'] == params


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_query_conditional_order(algo_client):
    await algo_client.query_conditional_order(client_order_id='order-id')
    kwargs = algo_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert algo_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/algo-orders/specific')
    assert kwargs['params'] == {
        'Signature': 'fY8erEcrmzD5Yb1in9nEKdrIXyJa1fuiKGFgctTcn7s=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'clientOrderId': 'order-id',
    }
