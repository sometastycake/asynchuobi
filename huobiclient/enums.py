from enum import Enum, IntEnum


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
    minepool = 'minepool'
    etf = 'etf'
    crypto_loans = 'crypto-loans'
    grid_trading = 'grid-trading'
    deposit_earning = 'deposit-earning'
    otc_options = 'otc-options'


class BalanceType(Enum):
    trade = 'trade'
    frozen = 'frozen'
    loan = 'loan'
    interest = 'interest'
    lock = 'lock'
    bank = 'bank'


class MarketStatus(IntEnum):
    normal = 1
    halted = 2
    cancel_only = 3


class MarketHaltReason(IntEnum):
    emergency_maintenance = 2
    scheduled_maintenance = 3


class AssetType(IntEnum):
    virtual_currency = 1
    fiat_currency = 2


class ChainType(Enum):
    plain = 'plain'
    live = 'live'
    old = 'old'
    new = 'new'
    legal = 'legal'
    tooold = 'tooold'


class InstrumentStatus(Enum):
    normal = 'normal'
    delisted = 'delisted'


class DepositStatus(Enum):
    allowed = 'allowed'
    prohibited = 'prohibited'


class WithdrawStatus(Enum):
    allowed = 'allowed'
    prohibited = 'prohibited'


class WithdrawFeeType(Enum):
    fixed = 'fixed'
    circulated = 'circulated'
    ratio = 'ratio'


class CandleInterval(Enum):
    min_1 = '1min'
    min_5 = '5min'
    min_15 = '15min'
    min_60 = '60min'
    hour_4 = '4hour'
    day_1 = '1day'
    mon_1 = '1mon'
    week_1 = '1week'
    year_1 = '1year'


class MarketDepth(Enum):
    step0 = 'step0'
    step1 = 'step1'
    step2 = 'step2'
    step3 = 'step3'
    step4 = 'step4'
    step5 = 'step5'


class TradeDirection(Enum):
    buy = 'buy'
    sell = 'sell'
