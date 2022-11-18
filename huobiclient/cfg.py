import os

HUOBI_SECRET_KEY: str = os.getenv(key='HUOBI_SECRET_KEY', default='')
HUOBI_ACCESS_KEY: str = os.getenv(key='HUOBI_ACCESS_KEY', default='')

HUOBI_API_URL: str = os.getenv(
    key='HUOBI_API_URL',
    default='https://api.huobi.pro',
)
HUOBI_WS_MARKET_URL: str = os.getenv(
    key='HUOBI_WS_MARKET_URL',
    default='wss://api.huobi.pro/ws',
)
HUOBI_WS_MARKET_FEED_URL: str = os.getenv(
    key='HUOBI_WS_MARKET_FEED_URL',
    default='wss://api.huobi.pro/feed',
)
HUOBI_WS_ASSET_AND_ORDER_URL: str = os.getenv(
    key='HUOBI_WS_ASSET_AND_ORDER_URL',
    default='wss://api.huobi.pro/ws/v2',
)
