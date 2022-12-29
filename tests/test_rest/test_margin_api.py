from datetime import datetime
from urllib.parse import urljoin

import pytest
from freezegun import freeze_time
from pydantic import ValidationError

from asynchuobi.enums import Sort
from asynchuobi.urls import HUOBI_API_URL
from tests.keys import HUOBI_ACCESS_KEY


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
