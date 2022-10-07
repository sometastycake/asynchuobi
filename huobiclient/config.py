from pydantic import BaseSettings


class BaseHuobiClientConfig(BaseSettings):

    HUOBI_SECRET_KEY: str
    HUOBI_ACCESS_KEY: str
    HUOBI_API_URL: str = 'https://api.huobi.pro'

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


huobi_client_config = BaseHuobiClientConfig()
