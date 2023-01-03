from datetime import datetime
from urllib.parse import urljoin

import pytest
from freezegun import freeze_time

from asynchuobi.api.clients.order import OrderHuobiClient
from asynchuobi.api.schemas import NewOrder
from asynchuobi.enums import Direct, OperatorCharacterOfStopPrice, OrderSide, OrderSource, OrderType
from asynchuobi.urls import HUOBI_API_URL
from tests.keys import HUOBI_ACCESS_KEY


@pytest.mark.asyncio
@pytest.mark.parametrize('access_key, secret_key', [('key', ''), ('', 'key')])
async def test_orders_api_wrong_keys(access_key, secret_key):
    with pytest.raises(ValueError):
        OrderHuobiClient(access_key=access_key, secret_key=secret_key)


@pytest.mark.asyncio
@pytest.mark.parametrize('order_type', [
    OrderType.buy_market,
    OrderType.sell_market,
    OrderType.buy_limit,
    OrderType.sell_limit,
])
@pytest.mark.parametrize('order_source', [
    OrderSource.spot_api,
    OrderSource.margin_api,
])
@pytest.mark.parametrize('operator', [
    None,
    OperatorCharacterOfStopPrice.gte,
    OperatorCharacterOfStopPrice.lte
])
@pytest.mark.parametrize('price', [None, 10.5])
@pytest.mark.parametrize('stop_price', [None, 20.5])
@pytest.mark.parametrize('client_order_id', [None, 'a456'])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_new_order(
        order_client, order_type, order_source, stop_price, operator, client_order_id, price
):
    await order_client.new_order(
        account_id=1,
        symbol='btcusdt',
        order_type=order_type,
        amount=1,
        price=price,
        source=order_source,
        stop_price=stop_price,
        operator=operator,
        client_order_id=client_order_id,
    )
    kwargs = order_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert order_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/orders/place')
    request = {
        'account-id': 1,
        'amount': 1.0,
        'type': order_type.value,
        'self-match-prevent': 0,
        'source': order_source.value,
        'symbol': 'btcusdt',
    }
    if stop_price is not None:
        request['stop-price'] = stop_price
    if client_order_id is not None:
        request['client-order-id'] = client_order_id
    if operator is not None:
        request['operator'] = operator.value
    if price is not None:
        request['price'] = price
    assert kwargs['json'] == request
    assert kwargs['params'] == {
        'Signature': 'Lh6NnZaA4C8hWKdjXgP5DJyAp4vGBgvwuviSHBc19dc=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('price', [None, 10.5])
@pytest.mark.parametrize('stop_price', [None, 10])
@pytest.mark.parametrize('operator', [
    None,
    OperatorCharacterOfStopPrice.gte,
    OperatorCharacterOfStopPrice.lte
])
@pytest.mark.parametrize('client_order_id', [None, 'client_order_id'])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_place_batch_of_orders(
        order_client, price, stop_price, operator, client_order_id
):
    await order_client.place_batch_of_orders(
        orders=[NewOrder(
            account_id=1,
            symbol='btcusdt',
            order_type=OrderType.buy_limit,
            amount=1,
            price=price,
            stop_price=stop_price,
            operator=operator,
            client_order_id=client_order_id,
        )],
    )
    kwargs = order_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert order_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/batch-orders')
    request = {
        'account-id': 1,
        'symbol': 'btcusdt',
        'type': OrderType.buy_limit.value,
        'self-match-prevent': 0,
        'source': OrderSource.spot_api.value,
        'amount': 1.0,
    }
    if price is not None:
        request['price'] = price
    if stop_price is not None:
        request['stop-price'] = stop_price
    if operator is not None:
        request['operator'] = operator.value
    if client_order_id is not None:
        request['client-order-id'] = client_order_id
    assert kwargs['json'] == [request]
    assert kwargs['params'] == {
        'Signature': 'HqsPxnqe+sCQ1mtSEbTCfObGtVib+sPCwMoq3uLhyw0=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('symbol', [None, 'btcusdt'])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_cancel_order(order_client, symbol):
    await order_client.cancel_order(
        order_id='1',
        symbol=symbol,
    )
    kwargs = order_client._requests.post.call_args.kwargs
    assert order_client._requests.post.call_count == 1
    assert len(kwargs) == 3
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/orders/1/submitcancel')
    request = {
        'order-id': '1',
    }
    if symbol is not None:
        request['symbol'] = symbol
    assert kwargs['json'] == request
    assert kwargs['params'] == {
        'Signature': 'PGMuhp9Civ0igcvOTUFanAehxfvWLcGelId9wJwT2NM=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_cancel_order_by_client_order_id(order_client):
    await order_client.cancel_order_by_client_order_id(
        client_order_id='1',
    )
    kwargs = order_client._requests.post.call_args.kwargs
    assert order_client._requests.post.call_count == 1
    assert len(kwargs) == 3
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/orders/submitCancelClientOrder')
    assert kwargs['json'] == {
        'client-order-id': '1',
    }
    assert kwargs['params'] == {
        'Signature': 'RsqkdFqvhLhYM/789snt6v3QBdeevWlhJ+zwFKzAvgQ=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'account_id,symbol,size,direct,start_order_id,side,signature', [
        (None, None, 1, None, None, None, 'Yy3IvQo/31lFk0/HWCUjBPL3SXGIvg/R09QduRTiqc8='),
        (1, None, 1, None, None, None, 'JWvmuu778U/7D8rtt5X1cPvDkCwKaovN3J9NV1F46Ts='),
        (None, 'btcusdt', 1, None, None, None, '/EklwbNiJsMum1HNcjWUiV8Uuut4PyUpZOWCINPYNxU='),
        (1, 'btcusdt', 100, Direct.next, 1, OrderSide.sell, '/V1AKXG06ge0fgr6SvoZ91zNVVdL4P7F8yjqLJ44kxo='),
        (None, 'btcusdt', 100, Direct.next, 1, OrderSide.sell, '4yCbWic5TBKOiTK7kUOe4WGf66StZsFNXsqTNl8JIgk='),
        (None, 'btcusdt', 1, None, None, None, '/EklwbNiJsMum1HNcjWUiV8Uuut4PyUpZOWCINPYNxU='),
        (1, 'btcusdt', 1, None, None, None, 'GapvaCRi9YM5hI9xA33S7LtWcQztx3doUi0TklJhFOQ='),
        (None, None, 1, Direct.prev, None, OrderSide.buy, 'j8VEmze5rMMeqIhh4aGwOdHjQTjYzE3/OYfqQrfRcmg='),
        (None, None, 1, Direct.next, None, None, 'hWuv5PoRMReU9/titT3htIolNU5Rt8yI/qdPY9Rpgdo='),
        (1, 'btcusdt', 1, Direct.next, None, OrderSide.buy, '57frngmSQfiYxxdqshb92OHxfMskm4qu2Qf+u8I5qm8='),
        (None, 'btcusdt', 1, Direct.next, None, OrderSide.sell, 'toHBFxirOIzZNfgOa03Dg5egChCsJQhGGp9S1+K8dwc='),
        (None, None, 100, Direct.next, 1, None, 'jCei6N5hdPUSCJG00987aYXfpX9uQg1CslvefUamPoE='),
        (None, None, 100, Direct.prev, 1, OrderSide.sell, 'yXc6z+QvcUBcK80IbJMvEtc794dISHSYtlZmE2qhoIY=')
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_all_open_orders(
        order_client, account_id, symbol, size, direct, start_order_id, side, signature
):
    await order_client.get_all_open_orders(
        account_id=account_id,
        symbol=symbol,
        size=size,
        direct=direct,
        start_order_id=start_order_id,
        side=side,
    )
    kwargs = order_client._requests.get.call_args.kwargs
    assert order_client._requests.get.call_count == 1
    assert len(kwargs) == 2
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/openOrders')
    request = {
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'Signature': signature,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'size': size,
    }
    if account_id is not None:
        request['account-id'] = account_id
    if direct is not None:
        request['direct'] = direct.value
    if side is not None:
        request['side'] = side.value  # type:ignore
    if start_order_id is not None:
        request['from'] = str(start_order_id)
    if symbol is not None:
        request['symbol'] = symbol
    assert kwargs['params'] == request


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [0, 501])
async def test_get_all_open_orders_wrong_size(order_client, size):
    with pytest.raises(ValueError):
        await order_client.get_all_open_orders(size=size)


@pytest.mark.asyncio
@pytest.mark.parametrize('account_id', [None, 1])
@pytest.mark.parametrize('symbols', [None, ['btcusdt', 'ethusdt'], ['btcusdc']])
@pytest.mark.parametrize('order_types', [
    None,
    [OrderType.buy_limit],
    [OrderType.buy_limit, OrderType.sell_limit],
])
@pytest.mark.parametrize('side', [OrderSide.buy, OrderSide.sell])
@pytest.mark.parametrize('size', [1, 100])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_batch_cancel_open_orders(
        order_client, account_id, symbols, order_types, side, size
):
    await order_client.batch_cancel_open_orders(
        account_id=account_id,
        symbols=symbols,
        order_types=order_types,
        side=side,
        size=size,
    )
    kwargs = order_client._requests.post.call_args.kwargs
    assert order_client._requests.post.call_count == 1
    assert len(kwargs) == 3
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/orders/batchCancelOpenOrders')
    request = {
        'size': size,
    }
    if account_id is not None:
        request['account-id'] = str(account_id)
    if side is not None:
        request['side'] = side.value
    if symbols is not None:
        request['symbol'] = ','.join(symbols)
    if order_types is not None:
        request['types'] = ','.join([str(order_type.value) for order_type in order_types])
    assert kwargs['json'] == request
    assert kwargs['params'] == {
        'Signature': 'u1sIQFk+GFaCCBdbQ9Dc2oE4yYz8R9QOPjk+1gzSPps=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [0, 101])
async def test_batch_cancel_open_orders_wrong_size(order_client, size):
    with pytest.raises(ValueError):
        await order_client.batch_cancel_open_orders(size=size)


@pytest.mark.asyncio
@pytest.mark.parametrize('symbols', [1, True])
async def test_batch_cancel_open_orders_wrong_symbols(order_client, symbols):
    with pytest.raises(TypeError):
        await order_client.batch_cancel_open_orders(symbols=symbols)


@pytest.mark.asyncio
@pytest.mark.parametrize('order_types', [1, True])
async def test_batch_cancel_open_orders_wrong_order_types(order_client, order_types):
    with pytest.raises(TypeError):
        await order_client.batch_cancel_open_orders(order_types=order_types)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'order_ids, client_order_ids', [
        (['1'], None),
        (None, ['1', '2'])
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_cancel_order_by_ids(order_client, order_ids, client_order_ids):
    await order_client.cancel_order_by_ids(
        order_ids=order_ids,
        client_order_ids=client_order_ids,
    )
    kwargs = order_client._requests.post.call_args.kwargs
    assert order_client._requests.post.call_count == 1
    assert len(kwargs) == 3
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/orders/batchcancel')
    request = {}
    if order_ids is not None:
        request['order-ids'] = order_ids
    if client_order_ids is not None:
        request['client-order-ids'] = client_order_ids
    assert kwargs['json'] == request
    assert kwargs['params'] == {
        'Signature': 'XnfPrcRrRO7e6ttLn7iwzV/C0dwqD1Of4EySZskG1gQ=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'order_ids, client_order_ids', [
        (None, 1),
        (1, None),
    ],
)
async def test_cancel_order_by_ids_order_ids_not_list(
        order_client, order_ids, client_order_ids,
):
    with pytest.raises(TypeError):
        await order_client.cancel_order_by_ids(
            order_ids=order_ids,
            client_order_ids=client_order_ids,
        )


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_dead_mans_switch(order_client):
    await order_client.dead_mans_switch(timeout=1)
    kwargs = order_client._requests.post.call_args.kwargs
    assert order_client._requests.post.call_count == 1
    assert len(kwargs) == 3
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/algo-orders/cancel-all-after')
    assert kwargs['json'] == {
        'timeout': 1
    }
    assert kwargs['params'] == {
        'Signature': 'YV/PR4WvcLLRV340xAzocPIrWXFcdjA9fCmzQlsSDv4=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_order_detail(order_client):
    await order_client.get_order_detail(order_id=1)
    kwargs = order_client._requests.get.call_args.kwargs
    assert order_client._requests.get.call_count == 1
    assert len(kwargs) == 2
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/orders/1')
    assert kwargs['params'] == {
        'Signature': 'hrLiWD2+gWnTEc1OW2SnOOTAIRuMYqIqOGtm/dHEiTg=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_order_detail_by_client_order_id(order_client):
    await order_client.get_order_detail_by_client_order_id(
        client_order_id=1
    )
    kwargs = order_client._requests.get.call_args.kwargs
    assert order_client._requests.get.call_count == 1
    assert len(kwargs) == 2
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/orders/getClientOrder')
    assert kwargs['params'] == {
        'Signature': 'Ls++IMQhqOMNoSB2osuZkjJiyokvPYsC2iMLX85YysI=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'clientOrderId': '1'
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_match_result_of_order(order_client):
    await order_client.get_match_result_of_order(order_id='1')
    kwargs = order_client._requests.get.call_args.kwargs
    assert order_client._requests.get.call_count == 1
    assert len(kwargs) == 2
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/orders/1/matchresults')
    assert kwargs['params'] == {
        'Signature': 'HDi4YN9iEQzu8irolQJFAg1qooljUjAud4YLxBDlGUU=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'states, order_types, size, direct, start_time, end_time, signature', [
        (['canceled', 'filled'], [OrderType.buy_limit, OrderType.sell_limit], 100, Direct.next, 1, 1,
         'iDS+gUx+MHTRle4TXKHyovIxKPUwZT+7JcNq6xMLts0='),
        (['filled'], [OrderType.buy_limit, OrderType.sell_limit], 100, Direct.next, 1, 1,
         'G4lzjjWu0in/FRaDO0eaXDW9rMiDwQE6fHjO6m6GUx0='),
        (['canceled', 'filled'], [OrderType.buy_limit], 100, Direct.next, 1, 1,
         '+YjGiN4600K4ERRW7XzmCzrpFHJ4UzbeGwNhbf0KZ68='),
        (['filled'], None, 1, None, None, None, 've2SLsQX7kJ2M4oZ5VBkWn6rIteOklCQI91sknzzw0o='),
        (['filled'], [OrderType.buy_limit], 1, None, None, None, '6W6pKayRiXLh/MQLfHLkkJSP5W7VyB2/G1btIZrObPg='),
        (['filled'], None, 1, Direct.prev, None, None, 'XKnEnBeh1Lrb5RAjM5jFDoHf1apDK5wTJq4DLFJBx5M='),
        (['filled'], [OrderType.buy_limit], 1, Direct.prev, None, None, 'HEw9+AVc6JqCQ2bzAqrR+Vft96yPQmT3QA0JvjoOLZI='),
        (['canceled', 'filled'], None, 100, Direct.next, None, None, 'PWn8bqoTV2AYSKixyiCF+14X7/gSxIoW6iaUBdk3Cw0='),
        (['filled'], [OrderType.buy_limit], 100, None, 1, None, '5/VsgUky0vNqdIfJ1C2HehnLLbnwyke5a1rtoq/dWk8='),
        (['filled'], None, 1, Direct.prev, 1, None, 'tF6kptJcQ3PWFRN6Fab8MvzW3r32RSUFmsQAbloiZOc=')
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_search_past_orders(
        order_client, states, order_types, size, direct, start_time, end_time, signature
):
    await order_client.search_past_orders(
        symbol='btcusdt',
        states=states,
        order_types=order_types,
        size=size,
        direct=direct,
        start_time_ms=start_time,
        end_time_ms=end_time,
    )
    kwargs = order_client._requests.get.call_args.kwargs
    assert order_client._requests.get.call_count == 1
    assert len(kwargs) == 2
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/orders')
    request = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'symbol': 'btcusdt',
        'states': ','.join(states),
        'size': size,
    }
    if order_types is not None:
        request['types'] = ','.join(map(lambda item: item.value, order_types))
    if direct is not None:
        request['direct'] = direct.value
    if start_time is not None:
        request['start-time'] = start_time
    if end_time is not None:
        request['end-time'] = end_time
    assert kwargs['params'] == request


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [0, 101])
async def test_search_past_orders_wrong_size(order_client, size):
    with pytest.raises(ValueError):
        await order_client.search_past_orders(
            symbol='btcusdt',
            states=['filled'],
            size=size,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('order_types', [1, True])
async def test_search_past_orders_wrong_order_types(order_client, order_types):
    with pytest.raises(TypeError):
        await order_client.search_past_orders(
            symbol='btcusdt',
            states=['filled'],
            order_types=order_types,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'symbol, start_time, end_time, direct, size, signature', [
        (None, None, None, Direct.prev, 10, 'FRd8vrJfYlU9OGx75iVSmfE8UIPZEOOT26XTq65rc5Q='),
        ('btcusdt', None, None, Direct.prev, 10, 'fVNfteNqBhFjC1EPV0lqaWmqnroPIpgby8xhWJVTFX4='),
        (None, 1, None, Direct.prev, 10, 'SqEoLtp3w8m+C8kAU8Dt8SapUfIHkde09RtljjDkaOI='),
        ('btcusdt', None, 1, Direct.next, 500, 'YeKwRdK7rBK7uIvwAUvc9vxmZNXuTuybRRUczMjQTFg='),
        (None, None, 1, Direct.next, 500, '/WHZ22i61cmAgAFbEvC0CO38LlDyX8pDA6aVzDlfotI='),
        (None, None, None, Direct.next, 500, 'bhmVINDzXxhAR5M0fu7fe91HbZa9hAlQutrPIk4y760='),
        (None, None, 1, Direct.next, 10, 'W0LAKhNmO25vqSmzn/deVGA6mUD014ukHYP/X+XaKrg='),
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_search_historical_orders_within_48_hours(
        order_client, symbol, start_time, end_time, direct, size, signature
):
    await order_client.search_historical_orders_within_48_hours(
        symbol=symbol,
        start_time_ms=start_time,
        end_time_ms=end_time,
        direct=direct,
        size=size
    )
    kwargs = order_client._requests.get.call_args.kwargs
    assert order_client._requests.get.call_count == 1
    assert len(kwargs) == 2
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/history')
    request = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'size': size,
        'direct': direct.value,
    }
    if symbol is not None:
        request['symbol'] = symbol
    if start_time is not None:
        request['start-time'] = start_time
    if end_time is not None:
        request['end-time'] = end_time
    assert kwargs['params'] == request


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [9, 1001])
async def test_search_historical_orders_within_48_hours_wrong_size(order_client, size):
    with pytest.raises(ValueError):
        await order_client.search_historical_orders_within_48_hours(
            size=size,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'order_types, start_time, end_time, from_order_id, direct, size, signature', [
        ([OrderType.buy_limit], None, None, None, Direct.next, 1, 'pei8V0Xn/GrS8WfLzOv2qbkfBGI6siDTfsbLyfnz9EE='),
        ([OrderType.buy_limit, OrderType.sell_limit], None, None, None, Direct.next, 1,
         'JTqx29NZ6AKtsupqd08o9DUAwCpQv3tyY/5mFmkylKQ='),
        ([OrderType.buy_limit], None, 1, None, Direct.next, 1, 'UisFcJAP1eGiPwFFKMdZAx2MDmqig+TCmMj1Uc7DdMQ='),
        ([OrderType.buy_limit], None, 1, 50, Direct.next, 1, '29aSUJwdXa4Gmyiq24QYCRY0y/XiRsKpl+guVECdTdI='),
        ([OrderType.buy_limit], 1, None, 50, Direct.next, 1, 'JNE1s6/a/44uxyZwmPqaoCiGDIx5cdoH3FpYinQv5dI='),
        ([OrderType.buy_limit], 1, 2, None, Direct.prev, 1, 'navO/z33Wbb5Ks9eBRjyAyEXlw0sqmS0h+/npWyJ8YI='),
        ([OrderType.buy_limit, OrderType.sell_limit], 1, 2, 50, Direct.prev, 500,
         'EBscqqYuQ3ZQ7gDJdy8bhDlm527GxGwGOGuI3Egoh4U='),
        ([OrderType.buy_limit], 1, 2, 50, Direct.prev, 500, 'NJQROonu//cFCf54iIV5NAGGOWn1jr5rSP7rEMx/JLU='),
        ([OrderType.buy_limit], None, None, 50, Direct.prev, 500, 'YVYclrPUzkfL4vypMz0kO/Plb8yPMIWYvJretRTAOVk=')
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_search_match_results(
        order_client, order_types, start_time, end_time, from_order_id, direct, size, signature
):
    await order_client.search_match_results(
        symbol='btcusdt',
        order_types=order_types,
        start_time_ms=start_time,
        end_time_ms=end_time,
        from_order_id=from_order_id,
        direct=direct,
        size=size,
    )
    kwargs = order_client._requests.get.call_args.kwargs
    assert order_client._requests.get.call_count == 1
    assert len(kwargs) == 2
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/order/matchresults')
    request = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'size': size,
        'direct': direct.value,
        'symbol': 'btcusdt',
    }
    if order_types is not None:
        request['types'] = ','.join(map(lambda item: item.value, order_types))
    if start_time is not None:
        request['start-time'] = start_time
    if end_time is not None:
        request['end-time'] = end_time
    if from_order_id is not None:
        request['from'] = str(from_order_id)
    assert kwargs['params'] == request


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [0, 501])
async def test_search_match_results_wrong_size(order_client, size):
    with pytest.raises(ValueError):
        await order_client.search_match_results(
            symbol='btcusdt',
            size=size,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('order_types', [1, True])
async def test_search_match_results_wrong_order_types(order_client, order_types):
    with pytest.raises(TypeError):
        await order_client.search_match_results(
            symbol='btcusdt',
            order_types=order_types,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('symbols, signature', [
    (('btcusdt',), 'KpdjqMnnrzFxDzornA45ADr4fHnjjdlruqucXqhG8r8='),
    (('btcusdt', 'ethusdt'), 'fmlXBQ609IREfm0RSs8B7o52byTKnViaa5J4v7Ss7e0=')
])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_current_fee_rate_applied_to_user(order_client, symbols, signature):
    await order_client.get_current_fee_rate_applied_to_user(
        symbols=symbols,
    )
    kwargs = order_client._requests.get.call_args.kwargs
    assert order_client._requests.get.call_count == 1
    assert len(kwargs) == 2
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/reference/transact-fee-rate')
    request = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'symbols': ','.join(symbols)
    }
    assert kwargs['params'] == request


@pytest.mark.asyncio
@pytest.mark.parametrize('symbols', [1, True])
async def test_get_current_fee_rate_applied_to_user_wrong_symbols(order_client, symbols):
    with pytest.raises(TypeError):
        await order_client.search_match_results(
            symbols=symbols,
        )
