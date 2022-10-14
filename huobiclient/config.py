from pydantic import BaseSettings, Field


class BaseHuobiClientConfig(BaseSettings):

    HUOBI_SECRET_KEY: str
    HUOBI_ACCESS_KEY: str
    HUOBI_API_URL: str = 'https://api.huobi.pro'

    HUOBI_WS_MARKET_URL: str = Field(
        default='wss://api.huobi.pro/ws',
        description='Websocket Market Feed (excluding MBP incremental channel & its REQ channel)',
    )

    HUOBI_WS_MARKET_FEED_URL: str = Field(
        default='wss://api.huobi.pro/feed',
        description='MBP incremental channel & its REQ channel',
    )

    HUOBI_WS_ASSET_AND_ORDER_URL: str = Field(
        default='wss://api.huobi.pro/ws/v2',
        description='Websocket Asset and Order',
    )

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


huobi_client_config = BaseHuobiClientConfig()
