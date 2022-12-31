from datetime import datetime
from urllib.parse import urljoin

import pytest
from freezegun import freeze_time
from pydantic import ValidationError

from asynchuobi.enums import Direct, Sort
from asynchuobi.urls import HUOBI_API_URL
from tests.keys import HUOBI_ACCESS_KEY


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_repay_margin_loan(margin_client):
    await margin_client.repay_margin_loan(
        account_id=1,
        currency='usdt',
        amount=1.0,
        transact_id='transact_id',
    )
    kwargs = margin_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert margin_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/account/repayment')
    assert kwargs['params'] == {
        'Signature': '0nNPYwL0cKe9ViuB0ylF1hvcY+c7m53reAHqUbsdOY4=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }
    assert kwargs['json'] == {
        'accountid': 1,
        'currency': 'usdt',
        'amount': 1.0,
        'transactId': 'transact_id',
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_transfer_asset_from_spot_to_isolated_margin_account(margin_client):
    await margin_client.transfer_asset_from_spot_to_isolated_margin_account(
        symbol='btcusdt',
        currency='usdt',
        amount=1.0,
    )
    kwargs = margin_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert margin_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/dw/transfer-in/margin')
    assert kwargs['params'] == {
        'Signature': 'zl+rlo8K59tuFwpMkzt/2WvdhgQCtWnLfL13zwuTQKY=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }
    assert kwargs['json'] == {'symbol': 'btcusdt', 'currency': 'usdt', 'amount': 1.0}


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_transfer_asset_from_isolated_margin_account_to_spot(margin_client):
    await margin_client.transfer_asset_from_isolated_margin_account_to_spot(
        symbol='btcusdt',
        currency='usdt',
        amount=1.0,
    )
    kwargs = margin_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert margin_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/dw/transfer-out/margin')
    assert kwargs['params'] == {
        'Signature': '71sP1aPnutMXNGgK8q9KKJzCWxjW04OP+cr8nSE/rr4=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }
    assert kwargs['json'] == {'symbol': 'btcusdt', 'currency': 'usdt', 'amount': 1.0}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'symbols, signature', [
        (None, 'E2+JeG50pGUbUpXkai8+lgApxi4gj4UJ6gpo3BIrWL0='),
        (('btcusdt', 'ethusdt'), 'R3OjeRLBEoi9t2mIXPzWJCTR11pmgj/aqtzMQOXU1Tg='),
    ],
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_isolated_loan_interest_rate_and_quota(margin_client, symbols, signature):
    await margin_client.get_isolated_loan_interest_rate_and_quota(
        symbols=symbols,
    )
    kwargs = margin_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert margin_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/margin/loan-info')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }
    if symbols is not None:
        params['symbols'] = ','.join(symbols)
    assert kwargs['params'] == params


@pytest.mark.asyncio
async def test_get_isolated_loan_interest_rate_and_quota_wrong_symbols(margin_client):
    with pytest.raises(TypeError):
        await margin_client.get_isolated_loan_interest_rate_and_quota(
            symbols=1,
        )


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_request_isolated_margin_loan(margin_client):
    await margin_client.request_isolated_margin_loan(
        symbol='btcusdt',
        currency='usdt',
        amount=1.0,
    )
    kwargs = margin_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert margin_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/margin/orders')
    assert kwargs['params'] == {
        'Signature': 'KEkNgpvmq54pDHQeMVUDCdPVd26yWfoJlPNlmHlFOVM=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }
    assert kwargs['json'] == {'symbol': 'btcusdt', 'currency': 'usdt', 'amount': 1.0}


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_repay_isolated_margin_loan(margin_client):
    await margin_client.repay_isolated_margin_loan(
        amount=1.0,
        loan_order_id='1',
    )
    kwargs = margin_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert margin_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/margin/orders/1/repay')
    assert kwargs['params'] == {
        'Signature': '4jOV/ntGBUpJFyFRDHmmHBnaqkI8MUz8LZO3DlGFA5s=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }
    assert kwargs['json'] == {'amount': 1.0}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'states, start_date, end_date, from_id, direct, sub_uid, signature', [
        (('a',), None, '2022-12-30', None, Direct.next, None, 'SfH/QHSkiSjTLIXInoo5+mUpj3mNRn/Mb+YxdqAZiYk='),
        (('a',), '2022-12-25', '2022-12-27', None, Direct.next, None, 't4LU+tRNvw5anCn9xJ31VnfKd6i38kixNuQ4ywr+VLw='),
        (('a', 'b'), '2022-12-25', None, None, Direct.prev, None, 'JUPSjWSDxho7EugQRlmKbOXvEKn0YFDS5/F+arNf7No='),
        (('a',), '2022-12-25', None, None, Direct.next, 1, 'mdX5W0YW1Bobyu1lD+Z8RkPgxQw/mZn0hbuQbej8ZoA='),
        (('a', 'b'), '2022-12-25', '2022-12-27', '1', Direct.prev, 1, 'IIVSBQLIfAEGmE73O4xSIpcc0thyXtbCtAaWkNBvVDQ='),
    ],
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_search_past_isolated_margin_orders(
        margin_client, states, start_date, end_date, from_id, direct, sub_uid, signature,
):
    await margin_client.search_past_isolated_margin_orders(
        symbol='btcusdt',
        states=states,
        start_date=start_date,
        end_date=end_date,
        from_order_id=from_id,
        direct=direct,
        sub_uid=sub_uid,
    )
    kwargs = margin_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert margin_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/margin/loan-orders')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'symbol': 'btcusdt',
        'size': 100,
    }
    if states is not None:
        params['states'] = ','.join(states)
    if from_id is not None:
        params['from'] = from_id
    if direct is not None:
        params['direct'] = direct.value
    if sub_uid is not None:
        params['sub-uid'] = sub_uid
    if start_date is not None:
        params['start-date'] = start_date
    if end_date is not None:
        params['end-date'] = end_date
    assert kwargs['params'] == params


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'symbol, size', [
        (1, 100),
        ('btcusdt', 0),
        ('btcusdt', 101),
        ('btcusdt', 'size'),
    ],
)
async def test_search_past_isolated_margin_orders_wrong_arguments(
        margin_client, symbol, size
):
    with pytest.raises(ValidationError):
        await margin_client.search_past_isolated_margin_orders(
            symbol=symbol,
            size=size,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('start_date, end_date', [(None, 1), (1, None), (1, 1)])
async def test_search_past_isolated_margin_orders_wrong_date(margin_client, start_date, end_date):
    with pytest.raises(TypeError):
        await margin_client.search_past_isolated_margin_orders(
            start_date=start_date,
            end_date=end_date,
            symbol='btcusdt',
        )


@pytest.mark.asyncio
async def test_search_past_isolated_margin_orders_wrong_states(margin_client):
    with pytest.raises(TypeError):
        await margin_client.search_past_isolated_margin_orders(
            symbol='btcusdt',
            states=[1, 2, 3],
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'symbol, sub_uid, signature', [
        (None, None, 'sN6RAiU8PGWrps9UE3bvauKvNOd7ZgMYd/mYiwftT9E='),
        ('btcusdt', None, 'gVqw0QfhvTZdCBxLEmM87Z+b6RpA9SAdD4cihJGr1qg='),
        (None, 1, 'NOr6Nxix9EVdp2RziRrdUq1tXfwpuT/12A+O9MVX4Sg='),
        ('btcusdt', 1, 'hskBAFGEjGicqwlQNV2ISkTlEaGPsP357Auutwxpj9A='),
    ],
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_balance_of_isolated_margin_account(margin_client, symbol, sub_uid, signature):
    await margin_client.get_balance_of_isolated_margin_account(symbol, sub_uid)
    kwargs = margin_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert margin_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/margin/accounts/balance')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }
    if symbol is not None:
        params['symbol'] = symbol
    if sub_uid is not None:
        params['sub-uid'] = sub_uid
    assert kwargs['params'] == params


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_transfer_asset_from_spot_to_cross_margin_account(margin_client):
    await margin_client.transfer_asset_from_spot_to_cross_margin_account(
        currency='usdt',
        amount=1.0,
    )
    kwargs = margin_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert margin_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/cross-margin/transfer-in')
    assert kwargs['params'] == {
        'Signature': 'WqEy3HXjalOObypdZbrACW1B8tgPZctetWBJ2vFTc18=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }
    assert kwargs['json'] == {'currency': 'usdt', 'amount': 1.0}


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_transfer_asset_from_cross_margin_to_spot_account(margin_client):
    await margin_client.transfer_asset_from_cross_margin_to_spot_account(
        currency='usdt',
        amount=1.0,
    )
    kwargs = margin_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert margin_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/cross-margin/transfer-out')
    assert kwargs['params'] == {
        'Signature': 'kAvXe3xREjlVRUieJPQyZkcp3jj68XO8CN23tMJhZqE=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }
    assert kwargs['json'] == {'currency': 'usdt', 'amount': 1.0}


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_cross_loan_interest_rate_and_quota(margin_client):
    await margin_client.get_cross_loan_interest_rate_and_quota()
    kwargs = margin_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert margin_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/cross-margin/loan-info')
    assert kwargs['params'] == {
        'Signature': 'WLzhZ49CJ10cTAfPxV/fFg8cMVCd6+51QrPR9M01Rl8=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_request_cross_margin_loan(margin_client):
    await margin_client.request_cross_margin_loan(
        currency='usdt',
        amount=1.0,
    )
    kwargs = margin_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert margin_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/cross-margin/orders')
    assert kwargs['params'] == {
        'Signature': 'uy0117FE4I754aQCwj0XhqD4nCA9/SsGDvtOmjm1jUU=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }
    assert kwargs['json'] == {'currency': 'usdt', 'amount': 1.0}


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_repay_cross_margin_loan(margin_client):
    await margin_client.repay_cross_margin_loan(
        loan_order_id='1',
        amount=1.0,
    )
    kwargs = margin_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert margin_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/cross-margin/orders/1/repay')
    assert kwargs['params'] == {
        'Signature': 'vyYdkK8F1OO05SDjsfFeDAvPWYEUO2lmBUn9lNIo3wo=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }
    assert kwargs['json'] == {'amount': 1.0}


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [9, 101])
async def test_search_past_cross_margin_orders_wrong_size(margin_client, size):
    with pytest.raises(ValueError) as error:
        await margin_client.search_past_cross_margin_orders(size=size)
    assert error.value.args[0] == f'Wrong size value "{size}"'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'start_date, end_date', [
        (None, 10),
        (10, None),
        (10, 10),
    ],
)
async def test_search_past_cross_margin_orders_wrong_date(margin_client, start_date, end_date):
    with pytest.raises(TypeError):
        await margin_client.search_past_cross_margin_orders(
            start_date=start_date,
            end_date=end_date,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'currency, state', [
        (None, 10),
        (10, None),
    ],
)
async def test_search_past_cross_margin_orders_wrong_types(
        margin_client, currency, state
):
    with pytest.raises(ValidationError):
        await margin_client.search_past_cross_margin_orders(
            currency=currency,
            state=state,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'currency, state, start_date, end_date, from_id, direct, sub_uid, signature', [
        (None, None, None, None, None, Direct.next, None,
         'KoIShQISf6EM0wsizmx6VzG3lWmiNpSrQ+ErQALYF/Q='),
        ('usdt', None, None, None, None, Direct.next, None,
         'Dtc570yfJTYtvO2FxA6oWdZbuSKhr88JHWXQwiq4Atc='),
        ('usdt', 'state', None, '2022-12-26', '1', Direct.next, None,
         'vMZpWxpxiC34S1xSUA+teQi/RWCorY9TAeSb9Xx1vKg='),
        (None, None, '2022-12-25', '2022-12-26', None, Direct.prev, None,
         'a1FmwoQTwwFkW9jjbtshLNdUMnwkKXZMQZQPl2unHfo='),
        (None, None, '2022-12-25', '2022-12-26', '1', Direct.prev, None,
         'yHACJxqrVTRul/K+4bbOcYm9kFwiSvlcrx5QOR+tHF8='),
        ('usdt', 'state', '2022-12-25', '2022-12-26', '1', Direct.prev, 20,
         'N90LQ/Efej8LVw20musyl/sSGQ/694corCkXODoAd+M=')
    ],
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_search_past_cross_margin_orders(
        margin_client, currency, state, start_date, end_date, from_id, direct, sub_uid, signature
):
    await margin_client.search_past_cross_margin_orders(
        currency=currency,
        state=state,
        start_date=start_date,
        end_date=end_date,
        from_order_id=from_id,
        direct=direct,
        sub_uid=sub_uid,
    )
    kwargs = margin_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert margin_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/cross-margin/loan-orders')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'size': 10,
    }
    if currency is not None:
        params['currency'] = currency
    if state is not None:
        params['state'] = state
    if start_date is not None:
        params['start-date'] = start_date
    if end_date is not None:
        params['end-date'] = end_date
    if from_id is not None:
        params['from'] = from_id
    if direct is not None:
        params['direct'] = direct.value
    if sub_uid is not None:
        params['sub-uid'] = sub_uid
    assert kwargs['params'] == params


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'sub_uid, signature', [
        (None, 'T/16f89fQhdEvBJko5wcXsaJfoe7mjRMY783mLY7WJE='),
        (1, 'ulcfvSZ/38KeuuBgA0Wg5o5IfqUE6DbhgJ6L+qkih8Q='),
    ],
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_balance_of_cross_margin_account(margin_client, sub_uid, signature):
    await margin_client.get_balance_of_cross_margin_account(sub_uid)
    kwargs = margin_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert margin_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/cross-margin/accounts/balance')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }
    if sub_uid is not None:
        params['sub-uid'] = sub_uid
    assert kwargs['params'] == params


@pytest.mark.asyncio
@pytest.mark.parametrize('limit', [0, 101])
async def test_repayment_record_reference_wrong_limit(margin_client, limit):
    with pytest.raises(ValueError) as error:
        await margin_client.repayment_record_reference(limit=limit)
    assert error.value.args[0] == f'Wrong limit value "{limit}"'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'currency, start_time, end_time, from_id', [
        (1, None, None, None),
        (None, '1', None, None),
        (None, None, '1', None),
        (None, None, None, '1'),
    ],
)
async def test_repayment_record_reference_wrong_argument_types(
        margin_client, currency, start_time, end_time, from_id,
):
    with pytest.raises(ValidationError):
        await margin_client.repayment_record_reference(
            currency=currency,
            start_time=start_time,
            end_time=end_time,
            from_id=from_id,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'account_id, currency, start_time, end_time, from_id, repay_id, sorting, signature', [
        (None, None, None, None, None, None, Sort.desc, 'k4D7mtyAJYiLSAowY+EITS/s+Ngo9j6HZOokWbw3uik='),
        (10, None, None, None, None, None, Sort.desc, 'Xgsvm9SCyKIEWifnSdYUXf3CA+wrEArjOpYUzKrrjuE='),
        (10, None, 1, 2, None, None, Sort.desc, 'aEJQQh4AXgiVeK+87+P3k8CL6aRzatMJ+LLcmBB/Rz4='),
        (None, 'usdt', 1, 2, 20, None, Sort.desc, 'zFKAxfjhlGaE+Hk1N8sxndLdeyCnOl9X1pjhCFs+ZCA='),
        (10, None, 1, 2, None, 30, Sort.desc, 'pocAMV4w0rdDghzYU8j5tKj6pgt56XTkER3XCP/I0g0='),
        (10, 'usdt', 1, 2, None, None, Sort.asc, '164JJFuFWFcLeZCHchevWfDa60/IdPK34jY7DKIQQ5s='),
        (10, 'usdt', 1, 2, 20, 30, Sort.asc, 't8zUCRuG+8uD47fzBFLUoJWvEVMUQxUBPJb253Xh9O8='),
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_repayment_record_reference(
        margin_client, account_id, currency, start_time, end_time, from_id, repay_id, sorting, signature
):
    await margin_client.repayment_record_reference(
        account_id=account_id,
        currency=currency,
        start_time=start_time,
        end_time=end_time,
        from_id=from_id,
        repay_id=repay_id,
        sorting=sorting,
    )
    kwargs = margin_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert margin_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/account/repayment')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'limit': 50,
    }
    if account_id is not None:
        params['accountId'] = account_id
    if currency is not None:
        params['currency'] = currency
    if start_time is not None:
        params['startTime'] = start_time
    if end_time is not None:
        params['endTime'] = end_time
    if from_id is not None:
        params['fromId'] = from_id
    if repay_id is not None:
        params['repayId'] = repay_id
    if sorting is not None:
        params['sort'] = sorting.value
    assert kwargs['params'] == params
