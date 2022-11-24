from datetime import datetime
from urllib.parse import urljoin

import pytest
from freezegun import freeze_time

from huobiclient.api.schemas import SubUser, SubUserCreation
from huobiclient.enums import (
    ApiKeyPermission,
    DeductMode,
    LockSubUserAction,
    MarginAccountActivation,
    MarginAccountType,
    Sort,
    TransferTypeBetweenParentAndSubUser,
)
from huobiclient.urls import HUOBI_API_URL


@pytest.mark.asyncio
@pytest.mark.parametrize('sub_uids', [{1}, (1, 2)])
@pytest.mark.parametrize('deduct_mode', [DeductMode.master, DeductMode.sub])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_set_deduction_for_parent_and_sub_user(subuser_client, sub_uids, deduct_mode):
    await subuser_client.set_deduction_for_parent_and_sub_user(
        sub_uids=sub_uids,
        deduct_mode=deduct_mode,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 4
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/deduct-mode')
    assert kwargs['method'] == 'POST'
    assert kwargs['json'] == {
        'subUids': ','.join([str(sub_uid) for sub_uid in sub_uids]),
        'deductMode': deduct_mode.value,
    }
    assert kwargs['params'] == {
        'Signature': 'HZQtpXz6A6FTKIA+5Q1K2MV3HuHzpNjYOW7VSyjd9H0=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('sub_uids', [1, True])
async def test_set_deduction_for_parent_and_sub_user_wrong_subuids(subuser_client, sub_uids):
    with pytest.raises(TypeError):
        await subuser_client.set_deduction_for_parent_and_sub_user(
            sub_uids=sub_uids,
            deduct_mode=DeductMode.master,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('access_key, signature', [
    (None, '8/+uLhrN2GoMYYr4bLAFG1/0OlKjRBDEmIOFgPW7gag='),
    ('1', 'P2BoqT5Z2V1u1OBU27nTfnN2S8yBewmqfB9UiQwHMI4=')
])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_api_key_query(subuser_client, access_key, signature):
    await subuser_client.api_key_query(
        uid=1,
        access_key=access_key,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/user/api-key')
    assert kwargs['method'] == 'GET'
    params = {
        'Signature': signature,
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'uid': 1,
    }
    if access_key is not None:
        params['accessKey'] = access_key
    assert kwargs['params'] == params


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_uid(subuser_client):
    await subuser_client.get_uid()
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/user/uid')
    assert kwargs['method'] == 'GET'
    assert kwargs['params'] == {
        'Signature': 'aNAXON0BI5Cg/rcmSRHW/Gsfrk1VwgK2FaE+QN6ukZw=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_sub_user_creation(subuser_client):
    await subuser_client.sub_user_creation(
        request=SubUserCreation(
            userList=[
                SubUser(userName='user 1', note='note'),
                SubUser(userName='user 2'),
            ],
        ),
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 4
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/creation')
    assert kwargs['method'] == 'POST'
    assert kwargs['json'] == {
        'userList': [
            {'userName': 'user 1', 'note': 'note'},
            {'userName': 'user 2'},
        ],
    }
    assert kwargs['params'] == {
        'Signature': 'lOAMO8Q1El2v3IiT4Ywc0P0TJbduR+oreHYmmYM0H+s=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('from_id, signature', [
    (None, 'OZdNU7IdglK3tTjM13kSD1KwTAGRHJ02rV/Hx0+Wa9Y='),
    (1, 'zmXUTWk0478MA0V8SBHfRpS0KlzwF6zAb3j/h7xFaT4='),
])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_sub_users_list(subuser_client, from_id, signature):
    await subuser_client.get_sub_users_list(
        from_id=from_id,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/user-list')
    assert kwargs['method'] == 'GET'
    params = {
        'Signature': signature,
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }
    if from_id is not None:
        params['fromId'] = from_id
    assert kwargs['params'] == params


@pytest.mark.asyncio
@pytest.mark.parametrize('action', [
    LockSubUserAction.lock, LockSubUserAction.unlock
])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_lock_unlock_sub_user(subuser_client, action):
    await subuser_client.lock_unlock_sub_user(
        sub_uid=1,
        action=action,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 4
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/management')
    assert kwargs['method'] == 'POST'
    assert kwargs['json'] == {
        'subUid': 1,
        'action': action.value,
    }
    assert kwargs['params'] == {
        'Signature': '3VkQrvWzUxXA4Zq4KZu586guHzw2r1HDaXQeiUiizLk=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_sub_user_status(subuser_client):
    await subuser_client.get_sub_user_status(
        sub_uid=1,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/user-state')
    assert kwargs['method'] == 'GET'
    assert kwargs['params'] == {
        'Signature': 'gGsMa2p5CgZ9DZKPZKaynAzyXFANmKmeJR7gB8TaGEk=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'subUid': 1,
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
@pytest.mark.parametrize('sub_uids', [{1}, {1, 2}])
@pytest.mark.parametrize('account_type', {
    MarginAccountType.cross_margin, MarginAccountType.isolated_margin,
})
@pytest.mark.parametrize('activation', [
    MarginAccountActivation.activated, MarginAccountActivation.deactivated,
])
async def test_set_tradable_market_for_sub_users(
        subuser_client, sub_uids, account_type, activation,
):
    await subuser_client.set_tradable_market_for_sub_users(
        sub_uids=sub_uids,
        account_type=account_type,
        activation=activation,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 4
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/tradable-market')
    assert kwargs['method'] == 'POST'
    assert kwargs['json'] == {
        'subUids': ','.join([str(sub_uid) for sub_uid in sub_uids]),
        'accountType': account_type.value,
        'activation': activation.value,
    }
    assert kwargs['params'] == {
        'Signature': 'oZGKnsqoyGXtHlBPQ2YvcXdot2V8g2OW0OSXB10LS+Y=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('sub_uids', [1, True])
async def test_set_tradable_market_for_sub_users_wrong_sub_uids(
        subuser_client, sub_uids,
):
    with pytest.raises(TypeError):
        await subuser_client.set_tradable_market_for_sub_users(
            sub_uids=sub_uids,
            account_type=MarginAccountType.cross_margin,
            activation=MarginAccountActivation.activated,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('sub_uids', [{1}, {1, 2}])
@pytest.mark.parametrize('transferrable', [True, False])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_set_asset_transfer_permission_for_sub_users(
        subuser_client, sub_uids, transferrable,
):
    await subuser_client.set_asset_transfer_permission_for_sub_users(
        sub_uids=sub_uids,
        transferrable=transferrable,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 4
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/transferability')
    assert kwargs['method'] == 'POST'
    assert kwargs['json'] == {
        'subUids': ','.join([str(sub_uid) for sub_uid in sub_uids]),
        'accountType': 'spot',
        'transferrable': str(transferrable).lower(),
    }
    assert kwargs['params'] == {
        'Signature': 'V75FYLYnhN8XK9HSS4ZIPDdHWu/vwLi8wP1jneug51k=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('sub_uids', [1, True])
async def test_set_asset_transfer_permission_for_sub_users_wrong_sub_uids(
        subuser_client, sub_uids,
):
    with pytest.raises(TypeError):
        await subuser_client.set_asset_transfer_permission_for_sub_users(
            sub_uids=sub_uids,
            transferrable=True,
        )


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_sub_users_account_list(subuser_client):
    await subuser_client.get_sub_users_account_list(
        sub_uid=1,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/account-list')
    assert kwargs['method'] == 'GET'
    assert kwargs['params'] == {
        'Signature': '4fH+UeoFpA+GLK3ZT/fDDv9GiXA47McfslTPcV4OulA=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'subUid': 1,
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
@pytest.mark.parametrize('permissions', [
    [ApiKeyPermission.readOnly],
    [ApiKeyPermission.readOnly, ApiKeyPermission.trade],
    [ApiKeyPermission.trade]
])
@pytest.mark.parametrize('ip_addresses', [
    None,
    {'1.1.1.1'},
    {'2.2.2.2', '1.1.1.1'}
])
@pytest.mark.parametrize('otp_token', [None, 'token'])
async def test_sub_user_api_key_creation(
        subuser_client, permissions, ip_addresses, otp_token,
):
    await subuser_client.sub_user_api_key_creation(
        sub_uid=1,
        note='note',
        permissions=permissions,
        ip_addresses=ip_addresses,
        otp_token=otp_token,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 4
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/api-key-generation')
    assert kwargs['method'] == 'POST'
    if ApiKeyPermission.readOnly not in permissions:
        permissions.append(ApiKeyPermission.readOnly)
    params = {
        'subUid': 1,
        'note': 'note',
        'permission': ','.join([str(perm.value) for perm in permissions]),
    }
    if ip_addresses is not None:
        params['ipAddresses'] = ','.join(ip_addresses)
    if otp_token is not None:
        params['otpToken'] = otp_token
    assert kwargs['json'] == params
    assert kwargs['params'] == {
        'Signature': 'LKG+yaQCmQ/FzGxF7xLoLj/uEnJmIVABL3IHMnf7qxw=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('permissions', [1, {1}, (1, 2)])
async def test_sub_user_api_key_creation_wrong_permissions(
        subuser_client, permissions,
):
    with pytest.raises(TypeError):
        await subuser_client.sub_user_api_key_creation(
            sub_uid=1,
            note='note',
            permissions=permissions,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('ip_addresses', [1, True])
async def test_sub_user_api_key_creation_wrong_ip_addresses(
        subuser_client, ip_addresses,
):
    with pytest.raises(TypeError):
        await subuser_client.sub_user_api_key_creation(
            sub_uid=1,
            note='note',
            permissions=[ApiKeyPermission.readOnly],
            ip_addresses=ip_addresses,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('permissions', [
    None,
    {ApiKeyPermission.readOnly},
    [ApiKeyPermission.readOnly, ApiKeyPermission.trade],
    [ApiKeyPermission.trade]
])
@pytest.mark.parametrize('ip_addresses', [
    None,
    {'1.1.1.1'},
    {'2.2.2.2', '1.1.1.1'}
])
@pytest.mark.parametrize('note', [None, 'note'])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_sub_user_api_key_modification(
        subuser_client, permissions, ip_addresses, note,
):
    await subuser_client.sub_user_api_key_modification(
        sub_uid=1,
        access_key='key',
        note=note,
        permissions=permissions,
        ip_addresses=ip_addresses,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 4
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/api-key-modification')
    assert kwargs['method'] == 'POST'
    params = {
        'subUid': 1,
        'accessKey': 'key',
    }
    if note is not None:
        params['note'] = note
    if permissions is not None:
        params['permission'] = ','.join([str(perm.value) for perm in permissions])
    if ip_addresses is not None:
        params['ipAddresses'] = ','.join(ip_addresses)
    assert kwargs['json'] == params
    assert kwargs['params'] == {
        'Signature': '1xkV0+eOpkRKVoqpPs9uyEL4nDrfa2wTCIYBEgnvwUU=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('permissions', [1, True])
async def test_sub_user_api_key_modification_wrong_permissions(
        subuser_client, permissions,
):
    with pytest.raises(TypeError):
        await subuser_client.sub_user_api_key_modification(
            sub_uid=1,
            access_key='key',
            permissions=permissions,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('ip_addresses', [1, True])
async def test_sub_user_api_key_modification_ip_addresses(
        subuser_client, ip_addresses,
):
    with pytest.raises(TypeError):
        await subuser_client.sub_user_api_key_modification(
            sub_uid=1,
            access_key='key',
            ip_addresses=ip_addresses,
        )


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_sub_user_api_key_deletion(subuser_client):
    await subuser_client.sub_user_api_key_deletion(
        sub_uid=1,
        access_key='key'
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 4
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/api-key-deletion')
    assert kwargs['method'] == 'POST'
    assert kwargs['json'] == {
        'subUid': 1,
        'accessKey': 'key',
    }
    assert kwargs['params'] == {
        'Signature': 'p1eIczo3gEifzlad6uDh4pCuI/LRvlm1dvhG4ypqsdU=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('transfer_type', [
    TransferTypeBetweenParentAndSubUser.master_transfer_in,
    TransferTypeBetweenParentAndSubUser.master_transfer_out,
])
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_transfer_asset_between_parent_and_sub_user(subuser_client, transfer_type):
    await subuser_client.transfer_asset_between_parent_and_sub_user(
        sub_uid=1,
        currency='btc',
        amount=1.0,
        transfer_type=transfer_type,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 4
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/subuser/transfer')
    assert kwargs['method'] == 'POST'
    assert kwargs['json'] == {
        'sub-uid': 1,
        'currency': 'btc',
        'amount': 1.0,
        'type': transfer_type.value,
    }
    assert kwargs['params'] == {
        'Signature': '+GbGqMqCQa8Lpk6nIMrUutrY35FoFARwnjf5gq1Ku4E=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_query_deposit_address_of_sub_user(subuser_client):
    await subuser_client.query_deposit_address_of_sub_user(
        sub_uid=1,
        currency='btc',
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/deposit-address')
    assert kwargs['method'] == 'GET'
    assert kwargs['params'] == {
        'Signature': 'i229f+09dxI08M3YyVHl0LqcKGSlQe4Om7KEVp8G/h8=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'currency': 'btc',
        'subUid': 1
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'currency, start_time, end_time, sorting, limit, from_id, signature', [
        (None, None, None, Sort.asc, 1, None, '4Lzxovkfuz+KZiYC0dHEjxGcjUCUFxBf29pSHCJcpkg='),
        ('btc', None, None, Sort.asc, 1, None, 'MS9hevd9X4grSsNMk6k+2rBRNhiUH9N4cUoNmb8DfCI='),
        (None, 1, None, Sort.asc, 1, None, 'PnLDwxL7hs5i7nf9Ewf3zpL8KKcxOfxOJLJ8tOVI5yo='),
        ('btc', 1, None, Sort.asc, 1, None, 'ZF4v1opyUwpXvfdU6hO6MWk9H4r9Pl90VLoiTytdNK0='),
        ('btc', 1, 1, Sort.asc, 1, 50, 'FboKpwjq5eGAtvFWOk64NTDVWZDTU2PtONfEkYer0U0='),
        ('btc', 1, 1, Sort.desc, 500, 50, 'Eqi1KlTQwQfZsmMG/EuxBoNhcMGTOKkUysG5fjGzgIc=')
    ]
)
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_query_deposit_history_of_sub_user(
        subuser_client, currency, start_time, end_time, sorting, limit, from_id, signature
):
    await subuser_client.query_deposit_history_of_sub_user(
        sub_uid=1,
        currency=currency,
        start_time=start_time,
        end_time=end_time,
        sorting=sorting,
        limit=limit,
        from_id=from_id,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v2/sub-user/query-deposit')
    assert kwargs['method'] == 'GET'
    params = {
        'Signature': signature,
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'limit': limit,
        'sort': sorting.value,
        'subUid': 1
    }
    if start_time is not None:
        params['startTime'] = start_time
    if end_time is not None:
        params['endTime'] = end_time
    if from_id is not None:
        params['fromId'] = from_id
    if currency is not None:
        params['currency'] = currency
    assert kwargs['params'] == params


@pytest.mark.asyncio
@pytest.mark.parametrize('limit', [0, 501])
async def test_query_deposit_history_of_sub_user_wrong_limit(
        subuser_client, limit,
):
    with pytest.raises(ValueError):
        await subuser_client.query_deposit_history_of_sub_user(
            sub_uid=1,
            limit=limit,
        )


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_aggregated_balance_of_all_sub_users(subuser_client):
    await subuser_client.get_aggregated_balance_of_all_sub_users()
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/subuser/aggregate-balance')
    assert kwargs['method'] == 'GET'
    assert kwargs['params'] == {
        'Signature': 'FzCcdDBsQh7p1nGKgqOGF/pDwKtf9tDPe8bNor7KJIU=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01'
    }


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_get_account_balance_of_sub_user(subuser_client):
    await subuser_client.get_account_balance_of_sub_user(
        sub_uid=1,
    )
    kwargs = subuser_client._rstrategy.request.call_args.kwargs
    assert len(kwargs) == 3
    assert subuser_client._rstrategy.request.call_count == 1
    assert kwargs['url'] == urljoin(HUOBI_API_URL, '/v1/account/accounts/1')
    assert kwargs['method'] == 'GET'
    assert kwargs['params'] == {
        'Signature': 'lmpg2TGL0UrUS6uxfHnJoVII3i5HkiSDR1NrsUJhquo=',
        'AccessKeyId': 'HUOBI_ACCESS_KEY',
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': '2023-01-01T00:01:01',
        'sub-uid': 1,
    }
