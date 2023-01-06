import gzip
import json

from aiohttp import WSMessage, WSMsgType

WS_MARKET_MESSAGES = [
    WSMessage(
        type=WSMsgType.BINARY,
        data=gzip.compress(
            data=json.dumps({
                'ping': 1,
            }).encode(),
        ),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=gzip.compress(
            data=json.dumps({
                'status': 'ok',
                'subbed': 'market.btcusdt.kline.1min',
                'ts': 1,
            }).encode(),
        ),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=gzip.compress(
            data=json.dumps({
                'ping': 2,
            }).encode(),
        ),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=gzip.compress(
            data=json.dumps({
                'ch': 'market.btcusdt.kline.1min',
                'ts': 1,
                'tick': {'open': 1},
            }).encode(),
        ),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=gzip.compress(
            data=json.dumps({
                'status': 'ok',
                'unsubbed': 'market.btcusdt.kline.1min',
                'ts': 1,
            }).encode(),
        ),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=gzip.compress(
            data=json.dumps({
                'status': 'error',
                'err-code': 'code',
                'err-msg': 'msg',
                'ts': 1,
            }).encode(),
        ),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.CLOSED,
        extra=None,
        data=None,
    ),
]

WS_MARKET_MESSAGES_WITHOUT_TOPIC = [
    WSMessage(
        type=WSMsgType.BINARY,
        data=gzip.compress(
            data=json.dumps({
                'ping': 1,
            }).encode(),
        ),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=gzip.compress(
            data=json.dumps({}).encode(),
        ),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.CLOSED,
        extra=None,
        data=None,
    ),
]
