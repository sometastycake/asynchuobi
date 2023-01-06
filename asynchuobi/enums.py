from enum import Enum, IntEnum


class CandleInterval(Enum):
    min_1 = '1min'
    min_5 = '5min'
    min_15 = '15min'
    min_30 = '30min'
    min_60 = '60min'
    hour_4 = '4hour'
    day_1 = '1day'
    mon_1 = '1mon'
    week_1 = '1week'
    year_1 = '1year'


class DepthLevel(Enum):
    step0 = 'step0'
    step1 = 'step1'
    step2 = 'step2'
    step3 = 'step3'
    step4 = 'step4'
    step5 = 'step5'


class PriceLevel(IntEnum):
    level_5 = 5
    level_10 = 10
    level_20 = 20


class AccountTypeCode(IntEnum):
    spot = 1
    isolated = 2
    cross = 3
    coin_futures = 4
    flat = 5
    minepool = 6
    coin_swaps = 7
    investment = 8
    borrow = 9
    earn = 10
    usdt_swaps = 11
    option = 12
    otc_options = 13
    crypto_loans = 14
    grid_trading = 15


class DeductMode(Enum):
    master = 'master'
    sub = 'sub'


class MarginAccountType(Enum):
    isolated_margin = 'isolated-margin'
    cross_margin = 'cross-margin'


class MarginAccountActivation(Enum):
    activated = 'activated'
    deactivated = 'deactivated'


class LockSubUserAction(Enum):
    lock = 'lock'
    unlock = 'unlock'


class ApiKeyPermission(Enum):
    readOnly = 'readOnly'
    trade = 'trade'


class Sort(Enum):
    asc = 'asc'
    desc = 'desc'


class TransferTypeBetweenParentAndSubUser(Enum):
    master_transfer_in = 'master-transfer-in'
    master_transfer_out = 'master-transfer-out'
    master_point_transfer_in = 'master-point-transfer-in'
    master_point_transfer_out = 'master-point-transfer-out'


class OrderType(Enum):
    buy_market = 'buy-market'
    sell_market = 'sell-market'
    buy_limit = 'buy-limit'
    sell_limit = 'sell-limit'
    buy_ioc = 'buy-ioc'
    sell_ioc = 'sell-ioc'
    buy_limit_maker = 'buy-limit-maker'
    sell_limit_maker = 'sell-limit-maker'
    buy_stop_limit = 'buy-stop-limit'
    sell_stop_limit = 'sell-stop-limit'
    buy_limit_fok = 'buy-limit-fok'
    sell_limit_fok = 'sell-limit-fok'
    buy_stop_limit_fok = 'buy-stop-limit-fok'
    sell_stop_limit_fok = 'sell-stop-limit-fok'


class ConditionalOrderType(Enum):
    limit = 'limit'
    market = 'market'


class OrderSource(Enum):
    spot_api = 'spot-api'
    margin_api = 'margin-api'
    super_margin_api = 'super-margin-api'
    c2c_margin_api = 'c2c-margin-api'


class OperatorCharacterOfStopPrice(Enum):
    gte = 'gte'
    lte = 'lte'


class OrderSide(Enum):
    buy = 'buy'
    sell = 'sell'


class Direct(Enum):
    next = 'next'  # noqa:VNE003
    prev = 'prev'


class MarketDepth(IntEnum):
    depth_5 = 5
    depth_10 = 10
    depth_20 = 20
