import os

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
HUOBI_WS_ACCOUNT_URL: str = os.getenv(
    key='HUOBI_WS_ACCOUNT_URL',
    default='wss://api.huobi.pro/ws/v2',
)
