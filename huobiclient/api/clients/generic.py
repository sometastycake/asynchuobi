from typing import Dict, Iterable, Optional
from urllib.parse import urljoin

from huobiclient.api.dto import _GetChainsInformationRequest, _GetMarketSymbolsSettings
from huobiclient.api.strategy.abstract import RequestStrategyAbstract
from huobiclient.api.strategy.request import BaseRequestStrategy
from huobiclient.urls import HUOBI_API_URL


class GenericHuobiClient:

    def __init__(
        self,
        api_url: str = HUOBI_API_URL,
        request_strategy: RequestStrategyAbstract = BaseRequestStrategy(),
    ):
        self._api = api_url
        self._rstrategy = request_strategy

    async def __aenter__(self) -> 'GenericHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    async def get_system_status(self) -> Dict:
        """
        This endpoint allows users to get system status, Incidents and planned maintenance
        https://huobiapi.github.io/docs/spot/v1/en/#get-system-status
        """
        return await self._rstrategy.request(
            url='https://status.huobigroup.com/api/v2/summary.json',
            method='GET',
            headers={
                'Content-Type': 'application/json',
            },
        )

    async def get_market_status(self) -> Dict:
        """
        The endpoint returns current market status
        https://huobiapi.github.io/docs/spot/v1/en/#get-market-status
        """
        return await self._rstrategy.request(
            method='GET',
            url=urljoin(self._api, '/v2/market-status')
        )

    async def get_all_supported_trading_symbols(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get all Supported Trading Symbol
        https://huobiapi.github.io/docs/spot/v1/en/#get-all-supported-trading-symbol-v2

        :param timestamp_milliseconds: timestamp to get incremental data
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self._rstrategy.request(
            method='GET',
            url=urljoin(self._api, '/v2/settings/common/symbols'),
            params=params,
        )

    async def get_all_supported_currencies(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get all Supported Currencies
        https://huobiapi.github.io/docs/spot/v1/en/#get-all-supported-currencies-v2

        :param timestamp_milliseconds: timestamp to get incremental data
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self._rstrategy.request(
            method='GET',
            url=urljoin(self._api, '/v2/settings/common/currencies'),
            params=params,
        )

    async def get_currencies_settings(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get Currencies Settings
        https://huobiapi.github.io/docs/spot/v1/en/#get-currencys-settings

        :param timestamp_milliseconds: timestamp to get incremental data
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self._rstrategy.request(
            method='GET',
            url=urljoin(self._api, '/v1/settings/common/currencys'),
            params=params,
        )

    async def get_symbols_settings(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get Symbols Settings
        https://huobiapi.github.io/docs/spot/v1/en/#get-symbols-setting

        :param timestamp_milliseconds: timestamp to get incremental data
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self._rstrategy.request(
            method='GET',
            url=urljoin(self._api, '/v1/settings/common/symbols'),
            params=params,
        )

    async def get_market_symbols_settings(
            self,
            symbols: Optional[Iterable[str]] = None,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get Market Symbols Setting
        https://huobiapi.github.io/docs/spot/v1/en/#get-market-symbols-setting

        :param symbols: symbols
        :param timestamp_milliseconds: timestamp to get incremental data
        """
        if symbols is not None and not isinstance(symbols, Iterable):
            raise TypeError(f'Iterable type expected for symbols, got "{type(symbols)}"')
        params = _GetMarketSymbolsSettings(
            ts=timestamp_milliseconds,
            symbols=','.join(symbols) if symbols else None,
        )
        return await self._rstrategy.request(
            method='GET',
            url=urljoin(self._api, '/v1/settings/common/market-symbols'),
            params=params.dict(exclude_none=True),
        )

    async def get_chains_information(
            self,
            show_desc: Optional[int] = None,
            timestamp_milliseconds: Optional[int] = None,
            currency: Optional[str] = None,
    ) -> Dict:
        """
        Get Chains Information
        https://huobiapi.github.io/docs/spot/v1/en/#get-chains-information

        :param show_desc: show desc, 0: no, 1: all, 2: suspend deposit/withdrawal and chain exchange
        :param timestamp_milliseconds: timestamp to get incremental data
        :param currency: currency
        """
        params = _GetChainsInformationRequest(
            show_desc=show_desc,
            ts=timestamp_milliseconds,
            currency=currency,
        )
        return await self._rstrategy.request(
            method='GET',
            url=urljoin(self._api, '/v1/settings/common/chains'),
            params=params.dict(by_alias=True, exclude_none=True),
        )

    async def get_chains_information_v2(
            self,
            currency: Optional[str] = None,
            authorized_user: bool = True,
    ) -> Dict:
        """
        API user could query static reference information for each currency,
        as well as its corresponding chain(s)
        https://huobiapi.github.io/docs/spot/v1/en/#apiv2-currency-amp-chains
        """
        params = {
            'authorizedUser': str(authorized_user).lower(),
        }
        if currency is not None:
            params['currency'] = currency.lower()
        return await self._rstrategy.request(
            method='GET',
            url=urljoin(self._api, '/v2/reference/currencies'),
            params=params,
        )

    async def get_current_timestamp(self) -> Dict:
        """
        This endpoint returns the current timestamp, i.e. the number of
        milliseconds that have elapsed since 00:00:00 UTC on 1 January 1970.
        https://huobiapi.github.io/docs/spot/v1/en/#get-current-timestamp
        """
        return await self._rstrategy.request(
            method='GET',
            url=urljoin(self._api, '/v1/common/timestamp'),
        )
