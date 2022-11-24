from enum import IntEnum


class TradeDetailMode(IntEnum):
    only_trade_event = 0
    trade_and_cancellation_events = 1
