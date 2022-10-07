from enum import Enum


class SymbolStatus(Enum):
    not_online = 'not-online'
    pre_online = 'pre-online'
    online = 'online'
    suspend = 'suspend'
    offline = 'offline'
    transfer_board = 'transfer-board'
    fuse = 'fuse'
