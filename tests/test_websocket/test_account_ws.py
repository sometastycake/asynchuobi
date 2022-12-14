import json
from datetime import datetime
from typing import Dict
from unittest.mock import AsyncMock

import pytest
from freezegun import freeze_time

from asynchuobi.exceptions import WSAuthenticateError, WSHuobiError, WSNotAuthenticated
from asynchuobi.urls import HUOBI_WS_ACCOUNT_URL
from asynchuobi.ws.enums import WSTradeDetailMode
from asynchuobi.ws.ws_client import WSHuobiAccount
from tests.keys import HUOBI_ACCESS_KEY, HUOBI_SECRET_KEY
from tests.test_websocket.stubs.connection import WSConnectionStub
from tests.test_websocket.stubs.ws_account_msg import WS_ACCOUNT_MESSAGES


@pytest.mark.parametrize(
    'access_key, secret_key', [
        ('', 'key'),
        ('key', ''),
        ('', ''),
    ]
)
def test_wrong_keys(account_ws, access_key, secret_key):
    with pytest.raises(ValueError):
        WSHuobiAccount(access_key=access_key, secret_key=secret_key)



def test_default_parameters(account_ws):
    assert account_ws._url == HUOBI_WS_ACCOUNT_URL
    assert account_ws._access_key == HUOBI_ACCESS_KEY
    assert account_ws._secret_key == HUOBI_SECRET_KEY
    assert account_ws._is_auth is False
    assert account_ws._loads == json.loads
    assert account_ws._callbacks == {}
    assert account_ws._run_callbacks_in_asyncio_tasks is False


@pytest.mark.asyncio
async def test_pong(account_ws):
    await account_ws._pong(1)
    account_ws._connection.send.assert_called_once_with({
        'action': 'pong',
        'data': {
            'ts': 1,
        },
    })


@pytest.mark.asyncio
async def test_close(account_ws, monkeypatch):
    monkeypatch.setattr(account_ws._connection, 'closed', False)
    await account_ws.close()
    account_ws._connection.close.assert_called_once()


@pytest.mark.asyncio
@freeze_time(datetime(2023, 1, 1, 0, 1, 1))
async def test_authorize(account_ws, monkeypatch):
    class Data:
        data = json.dumps({'code': 200})
    account_ws._connection.receive = AsyncMock(
        return_value=Data()
    )
    await account_ws.authorize()
    auth_message = {
        'action': 'req',
        'ch': 'auth',
        'params': {
            'authType': 'api',
            'accessKey': HUOBI_ACCESS_KEY,
            'signatureMethod': 'HmacSHA256',
            'signatureVersion': '2.1',
            'timestamp': '2023-01-01T00:01:01',
            'signature': '/bj24WJXtxcQbnOJel7jsWvVF7Nhm7QO3Y3hPZCgIb8='
        }
    }
    account_ws._connection.send.assert_called_once_with(auth_message)
    account_ws._connection.receive.assert_called_once_with()
    assert account_ws._is_auth is True


@pytest.mark.asyncio
async def test_authorize_error(account_ws, monkeypatch):
    class Data:
        data = json.dumps({'code': 2001, 'message': 'error'})
    account_ws._connection.receive = AsyncMock(
        return_value=Data()
    )
    with pytest.raises(WSAuthenticateError) as error:
        await account_ws.authorize()
    assert error.value.err_code == 2001
    assert error.value.err_msg == 'error'
    assert account_ws._is_auth is False


@pytest.mark.asyncio
async def test_subscribe_not_authenticated(account_ws):
    with pytest.raises(WSNotAuthenticated):
        await account_ws.subscribe('topic')


@pytest.mark.asyncio
async def test_subscribe_wrong_callback_type(account_ws):
    account_ws._is_auth = True
    with pytest.raises(TypeError):
        await account_ws.subscribe('topic', 10)


@pytest.mark.asyncio
async def test_subscribe(account_ws):
    def callback(message):
        ...

    account_ws._is_auth = True
    await account_ws.subscribe('topic', callback)
    account_ws._connection.send.assert_called_once_with({
        'action': 'sub',
        'ch': 'topic',
    })
    assert account_ws._callbacks == {'topic': callback}


@pytest.mark.asyncio
async def test_subscribe_without_callback(account_ws):
    account_ws._is_auth = True
    await account_ws.subscribe('topic')
    account_ws._connection.send.assert_called_once_with({
        'action': 'sub',
        'ch': 'topic',
    })
    assert account_ws._callbacks == {}


@pytest.mark.asyncio
async def test_subscribe_order_updates_wrong_symbol(account_ws):
    with pytest.raises(TypeError):
        await account_ws.subscribe_order_updates(10)


@pytest.mark.asyncio
async def test_subscribe_order_updates(account_ws):
    account_ws.subscribe = AsyncMock()
    await account_ws.subscribe_order_updates('btcusdt', None)
    account_ws.subscribe.assert_called_once_with(
        topic='orders#btcusdt',
        callback=None,
    )


@pytest.mark.asyncio
async def test_subscribe_trade_detail_wrong_symbol(account_ws):
    with pytest.raises(TypeError):
        await account_ws.subscribe_trade_detail(10)


@pytest.mark.asyncio
async def test_subscribe_trade_detail(account_ws):
    account_ws.subscribe = AsyncMock()
    mode = WSTradeDetailMode.only_trade_event
    await account_ws.subscribe_trade_detail(
        symbol='btcusdt',
        mode=mode,
        callback=None,
    )
    account_ws.subscribe.assert_called_once_with(
        topic='trade.clearing#btcusdt#0',
        callback=None,
    )


@pytest.mark.asyncio
async def test_subscribe_account_change(account_ws):
    account_ws.subscribe = AsyncMock()
    await account_ws.subscribe_account_change(mode=0)
    account_ws.subscribe.assert_called_once_with(
        topic='accounts.update#0',
        callback=None,
    )


@pytest.mark.asyncio
async def test_simple_reading_stream():
    ws = WSHuobiAccount(
        access_key=HUOBI_ACCESS_KEY,
        secret_key=HUOBI_SECRET_KEY,
        connection=WSConnectionStub,
        messages=WS_ACCOUNT_MESSAGES,
    )
    ws._is_auth = True
    await ws.subscribe_order_updates('*')
    await ws.subscribe_trade_detail('*')
    await ws.subscribe_account_change()
    received = []
    async for message in ws:
        received.append(message)
    assert received == [
        {'action': 'sub', 'code': 200, 'ch': 'orders#*', 'data': {}},
        {'action': 'sub', 'code': 200, 'ch': 'trade.clearing#*#0', 'data': {}},
        {'action': 'sub', 'code': 200, 'ch': 'accounts.update#0', 'data': {}},
        {'action': 'sub', 'code': 2001, 'ch': 'orders#-', 'message': 'invalid.ch'},
    ]
    assert ws._connection._sent_messages == [
        {'action': 'sub', 'ch': 'orders#*'},
        {'action': 'sub', 'ch': 'trade.clearing#*#0'},
        {'action': 'sub', 'ch': 'accounts.update#0'},
        {'action': 'pong', 'data': {'ts': 1}},
        {'action': 'pong', 'data': {'ts': 2}},
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize('is_async__call__', [True, False])
async def test_reading_stream_with_callbacks(is_async__call__):
    if is_async__call__:
        class Callback:
            received = []

            async def __call__(self, message: Dict):
                self.received.append(message)

        class Error:
            errors = []

            async def __call__(self, error: WSHuobiError):
                self.errors.append(error)
    else:
        class Callback:
            received = []

            def __call__(self, message: Dict):
                self.received.append(message)

        class Error:
            errors = []

            def __call__(self, error: WSHuobiError):
                self.errors.append(error)

    ws = WSHuobiAccount(
        access_key=HUOBI_ACCESS_KEY,
        secret_key=HUOBI_SECRET_KEY,
        connection=WSConnectionStub,
        messages=WS_ACCOUNT_MESSAGES,
    )
    ws._is_auth = True
    callback = Callback()
    await ws.subscribe_order_updates('*', callback=callback)
    await ws.subscribe_trade_detail('*', callback=callback)
    await ws.subscribe_account_change(callback=callback)
    await ws.run_with_callbacks(error_callback=Error())
    assert Callback.received == [
        {'action': 'sub', 'code': 200, 'ch': 'orders#*', 'data': {}},
        {'action': 'sub', 'code': 200, 'ch': 'trade.clearing#*#0', 'data': {}},
        {'action': 'sub', 'code': 200, 'ch': 'accounts.update#0', 'data': {}},
    ]
    assert ws._connection._sent_messages == [
        {'action': 'sub', 'ch': 'orders#*'},
        {'action': 'sub', 'ch': 'trade.clearing#*#0'},
        {'action': 'sub', 'ch': 'accounts.update#0'},
        {'action': 'pong', 'data': {'ts': 1}},
        {'action': 'pong', 'data': {'ts': 2}},
    ]
    assert len(Error.errors) == 1
    assert Error.errors[0].err_code == 2001
    assert Error.errors[0].err_msg == 'invalid.ch'


@pytest.mark.asyncio
async def test_reading_stream_callback_is_not_callable():
    ws = WSHuobiAccount(
        access_key=HUOBI_ACCESS_KEY,
        secret_key=HUOBI_SECRET_KEY,
        connection=WSConnectionStub,
        messages=WS_ACCOUNT_MESSAGES,
    )
    with pytest.raises(TypeError):
        await ws.run_with_callbacks(error_callback=10)  # type:ignore
