from huobiclient.schemas.base import BaseHuobiRequest


class SupportedTradingSymbolsRequest(BaseHuobiRequest):
    ts: int


class SupportedCurrenciesRequest(BaseHuobiRequest):
    ts: int
