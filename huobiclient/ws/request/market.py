import uuid
from typing import Dict

from huobiclient.enums import CandleInterval, MarketDepthAggregationLevel, PriceLevel
from huobiclient.ws.request.abstract import AbstractWebsocketRequest


class BaseMarketWS(AbstractWebsocketRequest):

    def __init__(self, symbol: str):
        self._symbol = symbol

    def topic(self) -> str:
        raise NotImplementedError

    def subscribe(self) -> Dict:
        return {'sub': self.topic, 'id': str(uuid.uuid4())}

    def unsubscribe(self) -> Dict:
        return {'unsub': self.topic, 'id': str(uuid.uuid4())}


class WSMarketCandle(BaseMarketWS):

    def __init__(self, symbol: str, interval: CandleInterval):
        super().__init__(symbol)
        self._interval = interval

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.kline.{self._interval.value}'


class WSMarketTicker(BaseMarketWS):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.ticker'


class WSMarketOrderbook(BaseMarketWS):

    def __init__(self, symbol: str, depth: MarketDepthAggregationLevel):
        super().__init__(symbol)
        self._depth = depth

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.depth.{self._depth.value}'


class WSMarketStats(BaseMarketWS):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.detail'


class WSMarketTradeDetail(BaseMarketWS):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.trade.detail'


class WSMarketBBO(BaseMarketWS):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.bbo'


class WSMarketETP(BaseMarketWS):

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.etp'


class WSMarketPriceRefreshUpdate(BaseMarketWS):

    def __init__(self, symbol: str, price_level: PriceLevel):
        super().__init__(symbol)
        self._price_level = price_level

    @property
    def topic(self) -> str:
        return f'market.{self._symbol}.mbp.refresh.{self._price_level.value}'
