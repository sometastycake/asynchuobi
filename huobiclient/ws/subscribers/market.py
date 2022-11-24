import uuid
from enum import Enum
from typing import Dict, Iterable

from huobiclient.enums import CandleInterval, MarketDepthAggregationLevel


class _SubscribeAction(Enum):
    sub = 'sub'
    unsub = 'unsub'


class BaseMarketStream:

    def __init__(self, symbols: Iterable[str]):
        self._symbols = symbols

    def _topic(self, symbol: str) -> str:  # noqa:U100
        raise NotImplementedError

    def _message(self, symbol: str, action: _SubscribeAction) -> Dict:
        return {action.value: self._topic(symbol), 'id': str(uuid.uuid4())}

    def subscribe(self):
        for symbol in self._symbols:
            yield self._message(symbol, _SubscribeAction.sub)

    def unsubscribe(self):
        for symbol in self._symbols:
            yield self._message(symbol, _SubscribeAction.unsub)


class TickerStream(BaseMarketStream):

    def _topic(self, symbol: str) -> str:
        return f'market.{symbol}.ticker'


class TradeDetailStream(BaseMarketStream):

    def _topic(self, symbol: str) -> str:
        return f'market.{symbol}.trade.detail'


class BestBidOfferStream(BaseMarketStream):

    def _topic(self, symbol: str) -> str:
        return f'market.{symbol}.bbo'


class MarketDetailStream(BaseMarketStream):

    def _topic(self, symbol: str) -> str:
        return f'market.{symbol}.detail'


class EtpStream(BaseMarketStream):

    def _topic(self, symbol: str) -> str:
        return f'market.{symbol}.etp'


class CandleStream(BaseMarketStream):

    def __init__(self, symbols: Iterable[str], interval: CandleInterval):
        super().__init__(symbols)
        self._interval = interval

    def _topic(self, symbol: str) -> str:
        return f'market.{symbol}.kline.{self._interval.value}'


class OrderbookStream(BaseMarketStream):

    def __init__(
        self,
        symbols: Iterable[str],
        aggregation_level: MarketDepthAggregationLevel = MarketDepthAggregationLevel.step0,
    ):
        super().__init__(symbols)
        self._aggregation_level = aggregation_level

    def _topic(self, symbol: str) -> str:
        return f'market.{symbol}.depth.{self._aggregation_level.value}'
