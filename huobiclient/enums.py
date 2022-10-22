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


class MarketDepthAggregationLevel(Enum):
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
