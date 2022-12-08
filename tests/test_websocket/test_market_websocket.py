import gzip
import json

import pytest

from asynchuobi.ws.enums import SubUnsub
from asynchuobi.ws.ws_client import HuobiMarketWebsocket, _default_message_id  # noqa


def test_default_parameters(market_websocket):
    assert market_websocket._loads == json.loads
    assert market_websocket._decompress == gzip.decompress
    assert market_websocket._default_message_id == _default_message_id
    assert market_websocket._raise_if_error is False
    assert market_websocket._run_callbacks_in_asyncio_tasks is True
    assert market_websocket._subscribed_ch == set()
    assert market_websocket._callbacks == {}


@pytest.mark.asyncio
async def test_context_manager():
    async with HuobiMarketWebsocket() as ws:
        assert ws._connection.closed is False


@pytest.mark.asyncio
async def test_pong(market_websocket):
    await market_websocket._pong(1)
    market_websocket._connection.send.assert_called_once_with({'pong': 1})


@pytest.mark.asyncio
async def test_close(market_websocket, monkeypatch):
    monkeypatch.setattr(market_websocket._connection, 'closed', False)
    await market_websocket.close()
    market_websocket._connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_unsubscribe_all(market_websocket, monkeypatch):
    monkeypatch.setattr(market_websocket, '_subscribed_ch', ['topic1', 'topic2'])
    monkeypatch.setattr(market_websocket._connection, 'closed', False)
    await market_websocket.unsubscribe_all()
    assert market_websocket._subscribed_ch == []
    assert len(market_websocket._connection.method_calls) == 2
    for call, topic in zip(market_websocket._connection.method_calls, ('topic1', 'topic2')):
        assert call.args[0] == {'unsub': topic}


@pytest.mark.asyncio
async def test_unsubscribe_all_with_closed_connection(market_websocket, monkeypatch):
    monkeypatch.setattr(market_websocket._connection, 'closed', True)
    await market_websocket.unsubscribe_all()
    assert market_websocket._connection.call_count == 0
    assert market_websocket._connection.await_count == 0


@pytest.mark.asyncio
async def test_handle_sub_unsub_wrong_action(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket._handle_sub_unsub('topic', 'action')


@pytest.mark.asyncio
async def test_handle_sub_unsub_wrong_callback(market_websocket):
    with pytest.raises(TypeError):
        await market_websocket._handle_sub_unsub(
            topic='topic',
            action=SubUnsub.sub,
            callback='callback',
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('message_id', [None, 'id'])
@pytest.mark.parametrize('topic', ['topic1', 'topic2'])
async def test_handle_sub_unsub_subscribe(market_websocket, message_id, topic):
    await market_websocket._handle_sub_unsub(
        topic=topic,
        action=SubUnsub.sub,
        message_id=message_id,
    )
    message = {SubUnsub.sub.value: topic}
    if message_id is not None:
        message['id'] = message_id
    market_websocket._connection.send.assert_called_once_with(message)
    assert topic in market_websocket._subscribed_ch


@pytest.mark.asyncio
async def test_handle_sub_unsub_unsubscribe(market_websocket, monkeypatch):
    monkeypatch.setattr(market_websocket, '_subscribed_ch', {'topic'})
    await market_websocket._handle_sub_unsub(
        topic='topic',
        action=SubUnsub.unsub,
    )
    message = {SubUnsub.unsub.value: 'topic'}
    market_websocket._connection.send.assert_called_once_with(message)
    assert market_websocket._subscribed_ch == set()
