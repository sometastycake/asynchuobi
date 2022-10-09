from typing import Any, Dict, Optional, Type, TypeVar

import aiohttp
from pydantic import BaseModel
from yarl import URL

from .config import huobi_client_config as config
from .schemas.account.response import AccountBalanceResponse, AccountsResponse
from .schemas.base import BaseHuobiRequest
from .schemas.common.request import GetChainsInformationRequest
from .schemas.common.response import (
    CurrentTimestampResponse,
    GetChainsInformationResponse,
    MarketStatusResponse,
    SupportedCurrenciesResponse,
    SupportedTradingSymbolsResponse,
    SystemStatusResponse,
)

ResponseModelType = TypeVar('ResponseModelType', bound=BaseModel)


class HuobiClient:

    def __init__(self):
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
            raise_for_status=True,
        )

    def __del__(self):
        if not self._session.closed:
            self._session.connector.close()

    def _url(self, path: str) -> str:
        return str(URL(config.HUOBI_API_URL).with_path(path))

    async def request(
            self,
            path: str,
            method: str,
            response_model: Type[ResponseModelType],
            params: Optional[Dict] = None,
            data: Optional[Any] = None,
    ) -> ResponseModelType:
        response = await self._session.request(
            url=self._url(path),
            method=method,
            params=params,
            data=data,
            headers={
                'Content-Type': 'application/json',
            },
        )
        return response_model.parse_raw(await response.text())

    async def get_current_timestamp(self) -> CurrentTimestampResponse:
        """
        This endpoint returns the current timestamp, i.e. the number of milliseconds that
        have elapsed since 00:00:00 UTC on 1 January 1970.
        """
        return await self.request(
            method='GET',
            path='/v1/common/timestamp',
            response_model=CurrentTimestampResponse,
        )

    async def get_market_status(self) -> MarketStatusResponse:
        """
        The endpoint returns current market status.
        """
        return await self.request(
            method='GET',
            path='/v2/market-status',
            response_model=MarketStatusResponse,
        )

    async def get_system_status(self) -> SystemStatusResponse:
        """
        This endpoint allows users to get system status, Incidents and planned maintenance.
        """
        response = await self._session.get(
            url='https://status.huobigroup.com/api/v2/summary.json',
            headers={
                'Content-Type': 'application/json',
            },
        )
        return SystemStatusResponse.parse_raw(await response.text())

    async def accounts(self) -> AccountsResponse:
        """
        Get all Accounts of the Current User.
        API Key Permission：Read.
        """
        path = '/v1/account/accounts'
        return await self.request(
            method='GET',
            path=path,
            params=BaseHuobiRequest().to_request(path, 'GET'),
            response_model=AccountsResponse,
        )

    async def account_balance(self, account_id: int) -> AccountBalanceResponse:
        """
        Get Account Balance of a Specific Account.
        API Key Permission：Read.
        """
        path = f'/v1/account/accounts/{account_id}/balance'
        return await self.request(
            method='GET',
            path=path,
            params=BaseHuobiRequest().to_request(path, 'GET'),
            response_model=AccountBalanceResponse,
        )

    async def get_all_supported_trading_symbols(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> SupportedTradingSymbolsResponse:
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
            response_model=SupportedTradingSymbolsResponse,
        )

    async def get_all_supported_currencies(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> SupportedCurrenciesResponse:
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
            response_model=SupportedCurrenciesResponse,
        )

    async def get_chains_information(
            self,
            show_desc: Optional[int] = None,
            timestamp_milliseconds: Optional[int] = None,
            currency: Optional[str] = None,
    ) -> GetChainsInformationResponse:
        """
        Get Chains Information.

        :param show_desc: show desc, 0: no, 1: all, 2: suspend deposit/withdrawal and chain exchange
        :param timestamp_milliseconds: timestamp to get incremental data
        :param currency: currency
        """
        request_data = GetChainsInformationRequest(
            show_desc=show_desc,
            ts=timestamp_milliseconds,
            currency=currency,
        )
        return await self.request(
            method='GET',
            path='/v1/settings/common/chains',
            params=request_data.dict(by_alias=True, exclude_none=True),
            response_model=GetChainsInformationResponse,
        )
