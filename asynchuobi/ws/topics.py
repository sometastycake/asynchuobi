from asynchuobi.enums import MarketDepthAggregationLevel as Aggregation


def market_candlestick_topic(symbol: str, interval: str) -> str:
    return f'market.{symbol}.kline.{interval}'


def ticker_topic(symbol: str) -> str:
    return f'market.{symbol}.ticker'


def market_depth_topic(symbol: str, level: Aggregation) -> str:
    return f'market.{symbol}.depth.{level.value}'


def bbo_topic(symbol: str) -> str:
    return f'market.{symbol}.bbo'


def trade_detail_topic(symbol: str) -> str:
    return f'market.{symbol}.trade.detail'


def market_detail_topic(symbol: str) -> str:
    return f'market.{symbol}.detail'


def etp_topic(symbol: str) -> str:
    return f'market.{symbol}.etp'
