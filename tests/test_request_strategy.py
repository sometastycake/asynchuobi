import asyncio

import pytest

from asynchuobi.api.request.strategy import BaseRequestStrategy


@pytest.mark.asyncio
async def test_get():
    req = BaseRequestStrategy()
    response = await req.get('https://httpbin.org/json')
    assert isinstance(response, dict)
    await req.close()
    with pytest.raises(RuntimeError) as error:
        await req.get('https://httpbin.org/json')
    assert error.value.args[0] == 'Session is closed'


@pytest.mark.asyncio
async def test_post():
    req = BaseRequestStrategy()
    response = await req.post('https://httpbin.org/post')
    assert isinstance(response, dict)
    await req.close()


@pytest.mark.asyncio
async def test_many_requests():
    req = BaseRequestStrategy(
        headers={
            'User-Agent': 'curl/7.64.1',
        },
        skip_auto_headers=(
            'Accept-Encoding',
        ),
    )

    async def task(value: int):
        return await req.post(
            url='https://httpbin.org/post',
            json={
                'value': value,
            },
            headers={
                'Accept': 'application/json',
            },
        )

    results = await asyncio.gather(
        task(0), task(1), task(2), task(3), task(4), task(5), task(6),
    )
    for i, result in enumerate(results):
        assert isinstance(result, dict)
        assert result['json'] == {'value': i}
        assert result['headers']['User-Agent'] == 'curl/7.64.1'
        assert result['headers']['Accept'] == 'application/json'
        assert 'Accept-Encoding' not in result['headers']

    await req.close()
