from pydantic import BaseSettings


class HuobiConfig(BaseSettings):

    HUOBI_SECRET_KEY: str
    HUOBI_ACCESS_KEY: str
    HUOBI_API_URL: str = 'https://api.huobi.pro'
    HUOBI_WS_MARKET_URL: str = 'wss://api.huobi.pro/ws'
    HUOBI_WS_MARKET_FEED_URL: str = 'wss://api.huobi.pro/feed'
    HUOBI_WS_ASSET_AND_ORDER_URL: str = 'wss://api.huobi.pro/ws/v2'
