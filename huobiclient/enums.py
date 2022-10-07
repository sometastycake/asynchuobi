from enum import Enum


class SymbolStatus(Enum):
    not_online = 'not-online'
    pre_online = 'pre-online'
    online = 'online'
    suspend = 'suspend'
    offline = 'offline'
    transfer_board = 'transfer-board'
    fuse = 'fuse'


class AccountState(Enum):
    working = 'working'
    lock = 'lock'


class AccountType(Enum):
    spot = 'spot'
    margin = 'margin'
    otc = 'otc'
    point = 'point'
    super_margin = 'super-margin'
    investment = 'investment'
    borrow = 'borrow'
    grid_trading = 'grid-trading'
    deposit_earning = 'deposit-earning'
    otc_options = 'otc-options'
