import os

HUOBI_SECRET_KEY: str = os.getenv('HUOBI_SECRET_KEY', None)
HUOBI_ACCESS_KEY: str = os.getenv('HUOBI_ACCESS_KEY', None)

HUOBI_API_URL: str = os.getenv('HUOBI_API_URL', 'https://api.huobi.pro')
HUOBI_WS_MARKET_URL: str = os.getenv('HUOBI_WS_MARKET_URL', 'wss://api.huobi.pro/ws')
HUOBI_WS_MARKET_FEED_URL: str = os.getenv('HUOBI_WS_MARKET_FEED_URL', 'wss://api.huobi.pro/feed')
HUOBI_WS_ASSET_AND_ORDER_URL: str = os.getenv('HUOBI_WS_ASSET_AND_ORDER_URL', 'wss://api.huobi.pro/ws/v2')
