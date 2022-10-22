from typing import Any, Dict, Optional

import aiohttp
from yarl import URL

from huobiclient.auth import APIAuth
from huobiclient.config import huobi_client_config as config
from huobiclient.enums import CandleInterval, MarketDepthAggregationLevel
from huobiclient.exceptions import HuobiError

from .dto import (
    _GetChainsInformationRequest,
    _GetMarketSymbolsSettings,
    _GetTotalValuation,
    _GetTotalValuationPlatformAssets,
)


class HuobiClient:

    def __init__(self, raise_if_status_error: bool = False):
        self._raise_if_status_error = raise_if_status_error
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
            raise_for_status=True,
        )

    def __del__(self):
        if not self._session.closed:
            self._session.connector.close()

    def _check_error(self, response: Dict) -> None:
        status = response.get('status')
        if isinstance(status, str) and status != 'ok':
            raise HuobiError(
                err_code=response.get('err-code', ''),
                err_msg=response.get('err-msg', ''),
            )

    def _url(self, path: str) -> str:
        return str(URL(config.HUOBI_API_URL).with_path(path))

    async def request(self, path: str, method: str, **kwargs: Any) -> Any:
        """
        Request to Huobi API.
        """
        response = await self._session.request(
            url=self._url(path),
            method=method,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        )
        data = await response.json()
        if self._raise_if_status_error and isinstance(data, dict):
            self._check_error(data)
        return data

    async def get_system_status(self) -> Dict:
        """
        This endpoint allows users to get system status, Incidents and planned maintenance.
        """
        response = await self._session.get(
            url='https://status.huobigroup.com/api/v2/summary.json',
            headers={
                'Content-Type': 'application/json',
            },
        )
        return await response.json()

    async def get_market_status(self) -> Dict:
        """
        The endpoint returns current market status.
        """
        return await self.request(method='GET', path='/v2/market-status')

    async def get_all_supported_trading_symbols(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get all Supported Trading Symbol.
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self.request(
            method='GET',
            path='/v2/settings/common/symbols',
            params=params,
        )

    async def get_all_supported_currencies(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get all Supported Currencies.
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self.request(
            method='GET',
            path='/v2/settings/common/currencies',
            params=params,
        )

    async def get_currencies_settings(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get Currencys Settings
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self.request(
            method='GET',
            path='/v1/settings/common/currencys',
            params=params,
        )

    async def get_symbols_settings(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get Currencys Settings
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self.request(
            method='GET',
            path='/v1/settings/common/symbols',
            params=params,
        )

    async def get_market_symbols_settings(
            self,
            symbols: Optional[str] = None,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get Currencys Settings
        """
        params = _GetMarketSymbolsSettings(
            ts=timestamp_milliseconds,
            symbols=symbols,
        )
        return await self.request(
            method='GET',
            path='/v1/settings/common/market-symbols',
            params=params.dict(exclude_none=True),
        )

    async def get_chains_information(
            self,
            show_desc: Optional[int] = None,
            timestamp_milliseconds: Optional[int] = None,
            currency: Optional[str] = None,
    ) -> Dict:
        """
        Get Chains Information.

        :param show_desc: show desc, 0: no, 1: all, 2: suspend deposit/withdrawal and chain exchange
        :param timestamp_milliseconds: timestamp to get incremental data
        :param currency: currency
        """
        params = _GetChainsInformationRequest(
            show_desc=show_desc,
            ts=timestamp_milliseconds,
            currency=currency,
        )
        return await self.request(
            method='GET',
            path='/v1/settings/common/chains',
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
        """
        params = {
            'authorizedUser': str(authorized_user).lower(),
        }
        if currency is not None:
            params['currency'] = currency.lower()
        return await self.request(
            method='GET',
            path='/v2/reference/currencies',
            params=params,
        )

    async def get_current_timestamp(self) -> Dict:
        """
        This endpoint returns the current timestamp, i.e. the number of
        milliseconds that have elapsed since 00:00:00 UTC on 1 January 1970.
        """
        return await self.request(method='GET', path='/v1/common/timestamp')

    async def get_candles(self, symbol: str, interval: CandleInterval, size: int = 150) -> Dict:
        """
        Market data APIs provide public market information such as varies of candlestick,
        depth and trade information.
        The market data is updated once per second.
        """
        if size < 1 or size > 2000:
            raise ValueError(f'Wrong value "{size}"')
        return await self.request(
            method='GET',
            path='/market/history/kline',
            params={
                'symbol': symbol,
                'period': interval.value,
                'size': size,
            },
        )

    async def get_latest_aggregated_ticker(self, symbol: str) -> Dict:
        """
        This endpoint retrieves the latest ticker with some important 24h
        aggregated market data.
        """
        return await self.request(
            method='GET',
            path='/market/detail/merged',
            params={
                'symbol': symbol,
            },
        )

    async def get_latest_tickers_for_all_pairs(self) -> Dict:
        """
        This endpoint retrieves the latest tickers for all supported pairs.
        """
        return await self.request(method='GET', path='/market/tickers')

    async def get_market_depth(
        self,
        symbol: str,
        depth: int = 20,
        aggregation_level: MarketDepthAggregationLevel = MarketDepthAggregationLevel.step0,
    ):
        """
        This endpoint retrieves the current order book of a specific pair.
        """
        if depth not in (5, 10, 20):
            raise ValueError(f'Wrong market depth value "{depth}"')
        return await self.request(
            method='GET',
            path='/market/depth',
            params={
                'symbol': symbol,
                'depth': depth,
                'type': aggregation_level.value,
            },
        )

    async def get_last_trade(self, symbol: str) -> Dict:
        """
        This endpoint retrieves the latest trade with its price,
        volume, and direction.
        """
        return await self.request(
            method='GET',
            path='/market/trade',
            params={
                'symbol': symbol,
            },
        )

    async def get_most_recent_trades(self, symbol: str, size: int = 1) -> Dict:
        """
        This endpoint retrieves the most recent trades with their price,
        volume, and direction.
        """
        if size < 1 or size > 2000:
            raise ValueError(f'Wrong value "{size}"')
        return await self.request(
            method='GET',
            path='/market/history/trade',
            params={
                'symbol': symbol,
                'size': size,
            },
        )

    async def get_last_market_summary(self, symbol: str) -> Dict:
        """
        This endpoint retrieves the summary of trading in the market
        for the last 24 hours.
        """
        return await self.request(
            method='GET',
            path='/market/detail/',
            params={
                'symbol': symbol,
            },
        )

    async def get_real_time_nav(self, symbol: str) -> Dict:
        """
        This endpoint returns real time NAV for ETP.
        """
        return await self.request(
            method='GET',
            path='/market/etp',
            params={
                'symbol': symbol,
            },
        )

    async def accounts(self) -> Dict:
        """
        Get all Accounts of the Current User.
        API Key Permission：Read.
        """
        path = '/v1/account/accounts'
        return await self.request(
            method='GET',
            path=path,
            params=APIAuth().to_request(path, 'GET'),
        )

    async def account_balance(self, account_id: int) -> Dict:
        """
        Get Account Balance of a Specific Account.
        API Key Permission：Read.
        """
        path = f'/v1/account/accounts/{account_id}/balance'
        return await self.request(
            method='GET',
            path=path,
            params=APIAuth().to_request(path, 'GET'),
        )

    async def get_total_valuation_of_platform_assets(
            self,
            account_type: Optional[str] = None,
            valuation_currency: Optional[str] = None,
    ) -> Dict:
        """
        Obtain the total asset valuation of the platform account according
        to the BTC or legal currency denominated unit.
        """
        params = _GetTotalValuationPlatformAssets(
            accountType=account_type,
            valuationCurrency=valuation_currency,
        )
        path = '/v2/account/valuation'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def get_asset_valuation(
            self,
            account_type: str,
            valuation_currency: Optional[str] = None,
            sub_uid: Optional[int] = None,
    ) -> Dict:
        """
        This endpoint returns the valuation of the total assets of
        the account in btc or fiat currency.
        """
        params = _GetTotalValuation(
            accountType=account_type,
            valuationCurrency=valuation_currency,
            subUid=sub_uid,
        )
        path = '/v2/account/asset-valuation'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )
