import uuid
from typing import Dict

from huobiclient.enums import CandleInterval, MarketDepth
from huobiclient.schemas.ws.abstract import AbstractWebsocketRequest


class BaseMarketWebsocketRequest(AbstractWebsocketRequest):

    def __init__(self, symbol: str):
        self._symbol = symbol

    def topic(self) -> str:
        raise NotImplementedError

    def subscribe(self) -> Dict:
        return {'sub': self.topic, 'id': str(uuid.uuid4())}

    def unsubscribe(self) -> Dict:
        return {'unsub': self.topic, 'id': str(uuid.uuid4())}


class MarketCandleRequest(BaseMarketWebsocketRequest):

    def __init__(self, symbol: str, interval: CandleInterval):
        super().__init__(symbol)
        self._interval = interval

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.kline.{self._interval.value}'


class MarketTickerRequest(BaseMarketWebsocketRequest):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.ticker'


class MarketOrderbookRequest(BaseMarketWebsocketRequest):

    def __init__(self, symbol: str, depth: MarketDepth):
        super().__init__(symbol)
        self._depth = depth

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.depth.{self._depth.value}'


class MarketDetailRequest(BaseMarketWebsocketRequest):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.detail'


class MarketTradeDetailRequest(BaseMarketWebsocketRequest):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.trade.detail'


class MarketBestBidOfferRequest(BaseMarketWebsocketRequest):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.bbo'
