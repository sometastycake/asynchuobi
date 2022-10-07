from typing import Any, Dict, Optional, Type, TypeVar

import aiohttp
from yarl import URL

from .config import huobi_client_config as config
from .schemas.account.response import AccountBalanceResponse, AccountsResponse
from .schemas.base import BaseHuobiRequest, BaseHuobiResponse
from .schemas.common.request import SupportedTradingSymbolsRequest
from .schemas.common.response import SupportedTradingSymbolsResponse

ResponseModelType = TypeVar('ResponseModelType', bound=BaseHuobiResponse)


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

    async def accounts(self) -> AccountsResponse:
        path = '/v1/account/accounts'
        return await self.request(
            method='GET',
            path=path,
            params=BaseHuobiRequest().to_request(path, 'GET'),
            response_model=AccountsResponse,
        )

    async def account_balance(self, account_id: int) -> AccountBalanceResponse:
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
        API Key Permission：Read.
        """
        path = '/v2/settings/common/symbols'
        if timestamp_milliseconds is not None:
            request = SupportedTradingSymbolsRequest(ts=timestamp_milliseconds)
        else:
            request = BaseHuobiRequest()
        return await self.request(
            method='GET',
            path=path,
            params=request.to_request(path, 'GET'),
            response_model=SupportedTradingSymbolsResponse,
        )
