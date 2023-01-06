from enum import IntEnum


class WSTradeDetailMode(IntEnum):
    only_trade_event = 0
    trade_and_cancellation_events = 1
