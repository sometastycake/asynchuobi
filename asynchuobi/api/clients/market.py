from typing import Dict
from urllib.parse import urljoin

from asynchuobi.api.request.abstract import RequestStrategyAbstract
from asynchuobi.api.request.strategy import BaseRequestStrategy
from asynchuobi.enums import CandleInterval, DepthLevel, MarketDepth
from asynchuobi.urls import HUOBI_API_URL


class MarketHuobiClient:

    def __init__(
        self,
        api_url: str = HUOBI_API_URL,
        request_strategy: RequestStrategyAbstract = BaseRequestStrategy(),
    ):
        self._api = api_url
        self._requests = request_strategy

    async def __aenter__(self) -> 'MarketHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._requests.close()

    async def get_candles(self, symbol: str, interval: CandleInterval, size: int = 150) -> Dict:
        """
        Market data APIs provide public market information such as varies of candlestick,
        depth and trade information
        The market data is updated once per second
        https://huobiapi.github.io/docs/spot/v1/en/#get-klines-candles

        :param symbol: The trading symbol to query
        :param interval: The period of each candle
        :param size: The number of data returns
        """
        if size < 1 or size > 2000:
            raise ValueError(f'Wrong size value "{size}"')
        return await self._requests.get(
            url=urljoin(self._api, '/market/history/kline'),
            params={
                'symbol': symbol,
                'period': interval.value,
                'size': size,
            },
        )

    async def get_latest_aggregated_ticker(self, symbol: str) -> Dict:
        """
        This endpoint retrieves the latest ticker with some important 24h
        aggregated market data
        https://huobiapi.github.io/docs/spot/v1/en/#get-latest-aggregated-ticker

        :param symbol: The trading symbol to query
        """
        return await self._requests.get(
            url=urljoin(self._api, '/market/detail/merged'),
            params={
                'symbol': symbol,
            },
        )

    async def get_latest_tickers_for_all_pairs(self) -> Dict:
        """
        This endpoint retrieves the latest tickers for all supported pairs
        https://huobiapi.github.io/docs/spot/v1/en/#get-latest-tickers-for-all-pairs
        """
        return await self._requests.get(
            url=urljoin(self._api, '/market/tickers'),
        )

    async def get_market_depth(
        self,
        symbol: str,
        depth: MarketDepth = MarketDepth.depth_20,
        aggregation_level: DepthLevel = DepthLevel.step0,
    ) -> Dict:
        """
        This endpoint retrieves the current order book of a specific pair
        https://huobiapi.github.io/docs/spot/v1/en/#get-market-depth

        :param symbol: The trading symbol to query
        :param depth: The number of market depth to return on each side
        :param aggregation_level: Market depth aggregation level
        """
        return await self._requests.get(
            url=urljoin(self._api, '/market/depth'),
            params={
                'symbol': symbol,
                'depth': depth.value,
                'type': aggregation_level.value,
            },
        )

    async def get_last_trade(self, symbol: str) -> Dict:
        """
        This endpoint retrieves the latest trade with its price,
        volume, and direction
        https://huobiapi.github.io/docs/spot/v1/en/#get-the-last-trade

        :param symbol: The trading symbol to query
        """
        return await self._requests.get(
            url=urljoin(self._api, '/market/trade'),
            params={
                'symbol': symbol,
            },
        )

    async def get_most_recent_trades(self, symbol: str, size: int = 1) -> Dict:
        """
        This endpoint retrieves the most recent trades with their price,
        volume, and direction
        https://huobiapi.github.io/docs/spot/v1/en/#get-the-most-recent-trades

        :param symbol: The trading symbol to query
        :param size: The number of data returns
        """
        if size < 1 or size > 2000:
            raise ValueError(f'Wrong size value "{size}"')
        return await self._requests.get(
            url=urljoin(self._api, '/market/history/trade'),
            params={
                'symbol': symbol,
                'size': size,
            },
        )

    async def get_last_market_summary(self, symbol: str) -> Dict:
        """
        This endpoint retrieves the summary of trading in the market
        for the last 24 hours
        https://huobiapi.github.io/docs/spot/v1/en/#get-the-last-24h-market-summary

        :param symbol: The trading symbol to query
        """
        return await self._requests.get(
            url=urljoin(self._api, '/market/detail/'),
            params={
                'symbol': symbol,
            },
        )

    async def get_real_time_nav(self, symbol: str) -> Dict:
        """
        This endpoint returns real time NAV for ETP
        https://huobiapi.github.io/docs/spot/v1/en/#get-real-time-nav

        :param symbol: ETP trading symbol
        """
        return await self._requests.get(
            url=urljoin(self._api, '/market/etp/'),
            params={
                'symbol': symbol,
            },
        )
