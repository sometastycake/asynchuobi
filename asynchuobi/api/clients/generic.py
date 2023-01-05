from typing import Dict, Iterable, Optional
from urllib.parse import urljoin

from asynchuobi.api.request.abstract import RequestStrategyAbstract
from asynchuobi.api.request.strategy import BaseRequestStrategy
from asynchuobi.api.schemas import _GetChainsInformation, _GetMarketSymbolsSettings
from asynchuobi.urls import HUOBI_API_URL


class GenericHuobiClient:

    def __init__(
        self,
        api_url: str = HUOBI_API_URL,
        requests: Optional[RequestStrategyAbstract] = None,
    ):
        self._api = api_url
        self._requests = requests if requests is not None else BaseRequestStrategy()

    async def __aenter__(self) -> 'GenericHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._requests.close()

    async def get_system_status(self) -> Dict:
        return await self._requests.get(
            url='https://status.huobigroup.com/api/v2/summary.json',
        )

    async def get_market_status(self) -> Dict:
        return await self._requests.get(
            url=urljoin(self._api, '/v2/market-status'),
        )

    async def get_all_supported_trading_symbols(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self._requests.get(
            url=urljoin(self._api, '/v2/settings/common/symbols'),
            params=params,
        )

    async def get_all_supported_currencies(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self._requests.get(
            url=urljoin(self._api, '/v2/settings/common/currencies'),
            params=params,
        )

    async def get_currencies_settings(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self._requests.get(
            url=urljoin(self._api, '/v1/settings/common/currencys'),
            params=params,
        )

    async def get_symbols_settings(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self._requests.get(
            url=urljoin(self._api, '/v1/settings/common/symbols'),
            params=params,
        )

    async def get_market_symbols_settings(
            self,
            symbols: Optional[Iterable[str]] = None,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        if symbols is not None and not isinstance(symbols, Iterable):
            raise TypeError(f'Iterable type expected for symbols, got "{type(symbols)}"')
        params = _GetMarketSymbolsSettings(
            ts=timestamp_milliseconds,
            symbols=','.join(symbols) if symbols else None,
        )
        return await self._requests.get(
            url=urljoin(self._api, '/v1/settings/common/market-symbols'),
            params=params.dict(exclude_none=True),
        )

    async def get_chains_information(
            self,
            show_desc: Optional[int] = None,
            timestamp_milliseconds: Optional[int] = None,
            currency: Optional[str] = None,
    ) -> Dict:
        params = _GetChainsInformation(
            show_desc=show_desc,
            ts=timestamp_milliseconds,
            currency=currency,
        )
        return await self._requests.get(
            url=urljoin(self._api, '/v1/settings/common/chains'),
            params=params.dict(by_alias=True, exclude_none=True),
        )

    async def get_chains_information_v2(
            self,
            currency: Optional[str] = None,
            authorized_user: bool = True,
    ) -> Dict:
        params = {
            'authorizedUser': str(authorized_user).lower(),
        }
        if currency is not None:
            params['currency'] = currency.lower()
        return await self._requests.get(
            url=urljoin(self._api, '/v2/reference/currencies'),
            params=params,
        )

    async def get_current_timestamp(self) -> Dict:
        return await self._requests.get(
            url=urljoin(self._api, '/v1/common/timestamp'),
        )
