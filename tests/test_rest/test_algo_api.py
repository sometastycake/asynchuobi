from datetime import datetime
from urllib.parse import urljoin

import pytest
from freezegun import freeze_time

from asynchuobi.enums import ConditionalOrderType, OrderSide
from asynchuobi.urls import HUOBI_API_URL
from tests.keys import HUOBI_ACCESS_KEY


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
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_query_conditional_order(algo_client):
    await algo_client.query_conditional_order(client_order_id='order-id')
    kwargs = algo_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert algo_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/algo-orders/specific')
    assert kwargs['params'] == {
        'Signature': 'fY8erEcrmzD5Yb1in9nEKdrIXyJa1fuiKGFgctTcn7s=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'clientOrderId': 'order-id',
    }
