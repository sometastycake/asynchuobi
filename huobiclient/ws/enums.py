from enum import Enum, IntEnum


class TradeDetailMode(IntEnum):
    only_trade_event = 0
    trade_and_cancellation_events = 1


class SubscribeAction(Enum):
    sub = 'sub'
    unsub = 'unsub'
