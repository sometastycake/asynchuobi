from enum import Enum, IntEnum


class WSTradeDetailMode(IntEnum):
    only_trade_event = 0
    trade_and_cancellation_events = 1


class SubUnsub(Enum):
    sub = 'sub'
    unsub = 'unsub'
