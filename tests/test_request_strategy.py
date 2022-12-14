import pytest

from asynchuobi.api.request.strategy import BaseRequestStrategy


@pytest.mark.asyncio
async def test_get():
    req = BaseRequestStrategy()
    response = await req.get('https://httpbin.org/json')
    assert isinstance(response, dict)


@pytest.mark.asyncio
async def test_post():
    req = BaseRequestStrategy()
    response = await req.post('https://httpbin.org/post')
    assert isinstance(response, dict)
