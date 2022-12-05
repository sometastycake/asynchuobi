from datetime import datetime
from urllib.parse import urljoin

import pytest
from freezegun import freeze_time

from asynchuobi.enums import AccountTypeCode, Sort
from asynchuobi.urls import HUOBI_API_URL
from tests.keys import HUOBI_ACCESS_KEY


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_accounts(account_client):
    await account_client.accounts()
    kwargs = account_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert account_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/account/accounts')
    assert kwargs['params'] == {
        'Signature': 'QlWgsW91USVj7HjtsmLShIb2V6FBbecprJBTKIRJ2e8=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_account_balance(account_client):
    await account_client.account_balance(account_id=1)
    kwargs = account_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert account_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/account/accounts/1/balance')
    assert kwargs['params'] == {
        'Signature': 'R/5i5DPhCzsBiTKrFif7rbNBRiBU3gws1gFQlbfXmEU=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('account_type_code, signature', [
    (None, 'tGv8X5+mh2A0Fobz/ijNFobwxwKqQku4h2yl+M2nHR0='),
    (AccountTypeCode.flat, '+p4/ZbhibAhVxVpdrJ5Lvu9PbX2e+GmQA75UEP2rPrg='),
    (AccountTypeCode.spot, 'Oq2C4pCCPMOL+Ngs5FlCzeHwsoYnmgFEOw8AAD2mvwI='),
])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_total_valuation_of_platform_assets(account_client, account_type_code, signature):
    await account_client.get_total_valuation_of_platform_assets(
        account_type_code=account_type_code,
    )
    kwargs = account_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert account_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/account/valuation')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'valuationCurrency': 'BTC'
    }
    if account_type_code is not None:
        params['accountType'] = account_type_code.value
    assert kwargs['params'] == params


@pytest.mark.asyncio
@pytest.mark.parametrize('currency, sub_uid, signature', [
    (None, None, '7Q8dp0tAWTXQiruP6e/d/8J0Vqwn2VRn9M0os4pD3Tc='),
    ('btc', None, '+yGktRWXg13Am63yv+k7oJr61xYqO+8ZCR179BjxAWc='),
    (None, 1, 'YUok9WAJHc9GiB1M19+vbgi0lr2XQWQlHhNxTPzMfHo='),
    ('btc', 1, 'SA9whYwLZpbaHcSs/yxuf7WxHC1USW8EWhNzqqmZEww=')
])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_asset_valuation(account_client, currency, sub_uid, signature):
    await account_client.get_asset_valuation(
        account_type='spot',
        valuation_currency=currency,
        sub_uid=sub_uid,
    )
    kwargs = account_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert account_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/account/asset-valuation')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'accountType': 'spot'
    }
    if currency is not None:
        params['valuationCurrency'] = 'BTC'
    if sub_uid is not None:
        params['subUid'] = sub_uid
    assert kwargs['params'] == params


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_asset_transfer(account_client):
    await account_client.asset_transfer(
        from_user=1,
        from_account_type='spot',
        from_account=2,
        to_user=3,
        to_account_type='spot',
        to_account=4,
        currency='btc',
        amount='1',
    )
    kwargs = account_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert account_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/account/transfer')
    assert kwargs['params'] == {
        'Signature': '2ZBuSF+pO5av3I0JKIVdmE1gZzxTyqShWbrNzosDB90=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }
    assert kwargs['json'] == {
        'amount': 1.0,
        'currency': 'btc',
        'from-account': 2,
        'from-account-type': 'spot',
        'from-user': 1,
        'to-account': 4,
        'to-account-type': 'spot',
        'to-user': 3
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'currency, transact_types, start_time, end_time, from_id, size, sorting, signature', [
        ('btc', ('trade',), None, None, None, 500, Sort.asc, '+oB+mzvnciZNEaHausOnbcv31yOZaxAhW5JrHj8pJ/E='),
        (None, ('trade', 'withdraw'), None, None, None, 500, Sort.asc, 'Ke7x68u5Qjk4PAvqOt9BDpOr+oE72OLXzUDatiSBwYk='),
        ('btc', ('trade', 'withdraw'), None, None, None, 500, Sort.asc, 'jvaV5GXKrbH6HWA24PatVzmv5l5dgF+UcoKqc2MGNOE='),
        (None, ('trade',), 200, 100, 1000, 500, Sort.asc, 'tW6KAYPBURg903tGQSHVgUMuRseLU8yh3nZR96arz8M='),
        ('btc', ('trade',), 200, 100, 1000, 500, Sort.asc, 'bwfnO7+Ud/9/xHtCzJdMhRyiuTaEZGtJeCc0f7QCPWo='),
        (None, ('trade', 'withdraw'), 200, 100, 1000, 500, Sort.asc, '+pe3fB5R7Ql2Rq5rwF9nNaC6k5zocpEU75z4/+IIw40='),
        ('btc', ('trade', 'withdraw'), 200, 100, 1000, 500, Sort.asc, 'hQBlXqka9mDn8+a08PU16tNpBwQdwgwn5sTrmYVS4IE='),
        ('btc', ('trade', 'withdraw'), 200, None, 1000, 500, Sort.desc, 'KNWlx0/euWW0ecyPqG8COyQIbv98DL+nKD6Nrx8gSkM='),
        ('btc', ('trade',), None, 100, None, 500, Sort.desc, 'kllghQUQ6GT8OSqPS9aXH35VEMfls8c75RLwCL583oo=')
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_account_history(
        account_client, currency, transact_types, start_time, end_time, from_id, size, sorting, signature
):
    await account_client.get_account_history(
        account_id=1,
        currency=currency,
        transact_types=transact_types,
        start_time=start_time,
        end_time=end_time,
        from_id=from_id,
        size=size,
        sorting=sorting,
    )
    kwargs = account_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert account_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/account/history')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'account-id': 1,
        'size': size,
        'transact-types': ','.join(transact_types),
        'sort': sorting.value
    }
    if currency is not None:
        params['currency'] = currency
    if start_time is not None:
        params['start-time'] = start_time
    if end_time is not None:
        params['end-time'] = end_time
    if from_id is not None:
        params['from-id'] = from_id
    assert kwargs['params'] == params


@pytest.mark.asyncio
@pytest.mark.parametrize('types', [1, True])
async def test_get_account_history_wrong_transact_types(account_client, types):
    with pytest.raises(TypeError):
        await account_client.get_account_history(
            account_id=1,
            transact_types=types,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [0, 501])
async def test_get_account_history_wrong_size(account_client, size):
    with pytest.raises(ValueError):
        await account_client.get_account_history(
            account_id=1,
            transact_types=('trade', ),
            size=size,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'currency, start_time, end_time, from_id, limit, sorting, signature', [
        (None, None, None, None, 1, Sort.asc, 'Ary4ArbLLtqxcUsdku/qu5CgZ9rVr4kU4E7nCwHPUjk='),
        ('btc', None, None, None, 1, Sort.asc, 'cTkLLgulYPIe/KtUZ8i+4x74pNAHx+9ycDBzbwBHtZM='),
        (None, 200, 100, 1000, 1, Sort.asc, 'fqVGknULosNBMTadLObD5bdRCTKj0HW15oWfyNdbGrI='),
        ('btc', 200, 100, 1000, 1, Sort.asc, 'CC75gj+sNKvk4FZpsYDBFMHkWKodfpHvwpikEhLHWgs='),
        ('btc', 200, None, 1000, 500, Sort.desc, 'N6Md+jsuYc18tqabqbnu0cgTy4tinhYrJUab48o/pOQ=')
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_account_ledger(
        account_client, currency, start_time, end_time, from_id, limit, sorting, signature
):
    await account_client.get_account_ledger(
        account_id=1,
        currency=currency,
        transact_types='transfer',
        start_time=start_time,
        end_time=end_time,
        from_id=from_id,
        limit=limit,
        sorting=sorting,
    )
    kwargs = account_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert account_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/account/ledger')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'accountId': 1,
        'limit': limit,
        'sort': sorting.value,
        'transactTypes': 'transfer'
    }
    if currency is not None:
        params['currency'] = currency
    if start_time is not None:
        params['startTime'] = start_time
    if end_time is not None:
        params['endTime'] = end_time
    if from_id is not None:
        params['fromId'] = from_id
    assert kwargs['params'] == params


@pytest.mark.asyncio
@pytest.mark.parametrize('limit', [0, 501])
async def test_get_account_ledger_wrong_limit(account_client, limit):
    with pytest.raises(ValueError):
        await account_client.get_account_ledger(
            account_id=1,
            limit=limit,
        )


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_transfer_fund_between_spot_and_futures(account_client):
    await account_client.transfer_fund_between_spot_and_futures(
        currency='btc',
        amount=1,
        transfer_type='futures-to-pro',
    )
    kwargs = account_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert account_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/futures/transfer')
    assert kwargs['json'] == {
        'currency': 'btc',
        'amount': 1.0,
        'type': 'futures-to-pro',
    }
    assert kwargs['params'] == {
        'Signature': '3JiFoPuH2PWPF6OXKvMtRleh+Tt7ebuMi5dEVuaaCcQ=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('sub_user_id, signature', [
    (None, 'HkdmPHG99UWNbubkEBGLR04fmH77/higXfrxHyMGfr8='),
    ('1', 'NaisJp3h6Rsji4s4Q3WEUkL6YlWrVIpuKzdVMS48/Es=')
])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_point_balance(account_client, sub_user_id, signature):
    await account_client.get_point_balance(sub_user_id=sub_user_id)
    kwargs = account_client._requests.get.call_args.kwargs
    assert len(kwargs) == 2
    assert account_client._requests.get.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/point/account')
    params = {
        'Signature': signature,
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }
    if sub_user_id is not None:
        params['subUid'] = sub_user_id
    assert kwargs['params'] == params


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_point_transfer(account_client):
    await account_client.point_transfer(
        from_uid='1',
        to_uid='2',
        group_id=3,
        amount=1
    )
    kwargs = account_client._requests.post.call_args.kwargs
    assert len(kwargs) == 3
    assert account_client._requests.post.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/point/transfer')
    assert kwargs['json'] == {
        'fromUid': '1',
        'toUid': '2',
        'groupId': 3,
        'amount': 1.0,
    }
    assert kwargs['params'] == {
        'Signature': 'e0hoJaZk/l+dWCrChzwaVnOcRb4YC3T3Efv6GQzwpzM=',
        'AccessKeyId': HUOBI_ACCESS_KEY,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }
