import json

from aiohttp import WSMessage, WSMsgType

WS_ACCOUNT_MESSAGES = [
    WSMessage(
        type=WSMsgType.BINARY,
        data=json.dumps({
            'action': 'ping',
            'data': {
                'ts': 1,
            },
        }),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=json.dumps({
            'action': 'sub',
            'code': 200,
            'ch': 'orders#*',
            'data': {},
        }),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=json.dumps({
            'action': 'sub',
            'code': 200,
            'ch': 'trade.clearing#*#0',
            'data': {}
        }),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=json.dumps({
            'action': 'ping',
            'data': {
                'ts': 2,
            },
        }),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=json.dumps({
            'action': 'sub',
            'code': 200,
            'ch': 'accounts.update#0',
            'data': {}
        }),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.BINARY,
        data=json.dumps({
            'action': 'sub',
            'code': 2001,
            'ch': 'orders#-',
            'message': 'invalid.ch'
        }),
        extra=None,
    ),
    WSMessage(
        type=WSMsgType.CLOSED,
        extra=None,
        data=None,
    ),
]
