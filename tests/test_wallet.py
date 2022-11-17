from datetime import datetime
from urllib.parse import urljoin

import pytest
from freezegun import freeze_time

from huobiclient.cfg import HUOBI_API_URL
from huobiclient.enums import Direct


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_query_deposit_address(wallet_client):
    await wallet_client.query_deposit_address(
        currency='btc',
    )
    kwargs = wallet_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert wallet_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/account/deposit/address')
    assert kwargs['method'] == 'GET'
    assert kwargs['params'] == {
        'Signature': 'CUqQMYGXm8jU1SnPFcFR+wHi90ONFqSJl2HGFCkdu2U=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'currency': 'btc'
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_query_withdraw_quota(wallet_client):
    await wallet_client.query_withdraw_quota(
        currency='btc',
    )
    kwargs = wallet_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert wallet_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/account/withdraw/quota')
    assert kwargs['method'] == 'GET'
    assert kwargs['params'] == {
        'Signature': 'EJ4O26ecnb3VgRvuBg0pvtugEzoWONgScKHcHHgu1YA=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'currency': 'btc'
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'chain, note, limit, from_id, signature', [
        (None, None, 1, None, '/hYwVsEVkX2sOBzhkqz11dgmM47RjX31CrglEQiV9Rw='),
        ('chain', None, 1, None, 'nc8BU8UQqp+ov05gNeu8dBsB9TV3pF2nw14rObKAPPM='),
        (None, 'note', 1, None, '7PgvdwSKSGMM2eEFPxt7LPmC2Y13sRftVkJ07jbsS5A='),
        ('chain', 'note', 1, None, 'YUpOynlMb4oEQ+SkMspyAW4gMt0dAzIS/yUAuicr5sA='),
        ('chain', 'note', 500, 10, 'wVOgi+lsc5GyXq1VrkoFaUKS4sKqpWragsOHfsD0tzA=')
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_query_withdraw_address(wallet_client, chain, note, limit, from_id, signature):
    await wallet_client.query_withdraw_address(
        currency='btc',
        chain=chain,
        note=note,
        limit=limit,
        from_id=from_id,
    )
    kwargs = wallet_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert wallet_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/account/withdraw/address')
    assert kwargs['method'] == 'GET'
    params = {
        'Signature': signature,
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'currency': 'btc',
        'limit': limit,
    }
    if chain is not None:
        params['chain'] = chain
    if note is not None:
        params['note'] = note
    if from_id is not None:
        params['fromId'] = from_id
    assert kwargs['params'] == params


@pytest.mark.asyncio
@pytest.mark.parametrize('limit', [0, 501])
async def test_query_withdraw_address_wrong_limit(wallet_client, limit):
    with pytest.raises(ValueError):
        await wallet_client.query_withdraw_address(
            currency='btc',
            limit=limit,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('fee', [None, 2])
@pytest.mark.parametrize('chain', [None, 'chain'])
@pytest.mark.parametrize('addr_tag', [None, 'tag'])
@pytest.mark.parametrize('client_order_id', [None, 'id'])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_create_withdraw_request(
        wallet_client, fee, chain, addr_tag, client_order_id
):
    await wallet_client.create_withdraw_request(
        address='address',
        currency='btc',
        amount=1,
        fee=fee,
        chain=chain,
        addr_tag=addr_tag,
        client_order_id=client_order_id
    )
    kwargs = wallet_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 4
    assert wallet_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/dw/withdraw/api/create')
    assert kwargs['method'] == 'POST'
    data = {
        'address': 'address',
        'currency': 'btc',
        'amount': 1.0,
    }
    if fee is not None:
        data['fee'] = fee
    if chain is not None:
        data['chain'] = chain
    if addr_tag is not None:
        data['addr-tag'] = addr_tag
    if client_order_id is not None:
        data['client-order-id'] = client_order_id
    assert kwargs['json'] == data
    assert kwargs['params'] == {
        'Signature': '5x3R4I/B0Ig8A8LPrHlyraN5ltcwgskF9XhOEq3sCQ8=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_cancel_withdraw_request(wallet_client):
    await wallet_client.cancel_withdraw_request(
        withdraw_id=1,
    )
    kwargs = wallet_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert wallet_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/dw/withdraw-virtual/1/cancel')
    assert kwargs['method'] == 'POST'
    assert kwargs['params'] == {
        'Signature': '3mZpCvPLJfswHNyixuBtKkm1lTLCvTTcA2GjadB+EBI=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'currency, from_transfer_id, size, direct, signature', [
        (None, None, 1, Direct.prev, 'BOhNZ49nXff7a2VsM3ypGeCWGI8/EScZaNpOzkQl4Ps='),
        ('btc', None, 1, Direct.prev, '8rw6WgZe8hO0Nn5lgPpgbWFA9D8mjlEZ5DNnP3hqR/8='),
        (None, 'transfer_id', 1, Direct.prev, 'VY72SvD7o14eGf1j/B/l8/n9yiFzm8NPX+guhgmTYuw='),
        ('btc', 'transfer_id', 1, Direct.prev, '/rH49Os+q3HzOwCJtYqPKfCdKQzPAWAOcXomv1Us+HU='),
        ('btc', 'transfer_id', 500, Direct.next, '+fEgtnQpXAZHLiqNaZW7dH1TwxOf6dvNLQ3TtKKgR0A=')
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_search_for_existed_withraws_and_deposits(
        wallet_client, currency, from_transfer_id, size, direct, signature
):
    await wallet_client.search_for_existed_withraws_and_deposits(
        transfer_type='type',
        currency=currency,
        from_transfer_id=from_transfer_id,
        size=size,
        direct=direct,
    )
    kwargs = wallet_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert wallet_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/query/deposit-withdraw')
    assert kwargs['method'] == 'GET'
    params = {
        'Signature': signature,
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'direct': direct.value,
        'size': size,
        'type': 'type',
    }
    if currency is not None:
        params['currency'] = currency
    if from_transfer_id is not None:
        params['from'] = from_transfer_id
    assert kwargs['params'] == params


@pytest.mark.asyncio
@pytest.mark.parametrize('size', [0, 501])
async def test_search_for_existed_withraws_and_deposits_wrong_size(wallet_client, size):
    with pytest.raises(ValueError):
        await wallet_client.search_for_existed_withraws_and_deposits(
            transfer_type='type',
            size=size,
        )
