from typing import Dict, Optional
from urllib.parse import urljoin

from asynchuobi.api.schemas import (
    _CreateWithdrawRequest,
    _QueryDepositAddress,
    _QueryWithdrawAddress,
    _QueryWithdrawalOrderByClientOrderId,
    _QueryWithdrawQuota,
    _SearchExistedWithdrawsAndDeposits,
)
from asynchuobi.api.strategy.abstract import RequestStrategyAbstract
from asynchuobi.api.strategy.request import BaseRequestStrategy
from asynchuobi.auth import APIAuth
from asynchuobi.enums import Direct
from asynchuobi.urls import HUOBI_API_URL


class WalletHuobiClient:

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        api_url: str = HUOBI_API_URL,
        request_strategy: RequestStrategyAbstract = BaseRequestStrategy(),
    ):
        if not access_key or not secret_key:
            raise ValueError('Access key or secret key can not be empty')
        self._api = api_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._rstrategy = request_strategy

    async def __aenter__(self) -> 'WalletHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._rstrategy.close()

    async def query_deposit_address(self, currency: str) -> Dict:
        """
        Parent user and sub user could query deposit address of corresponding chain,
        for a specific cryptocurrency (except IOTA)
        https://huobiapi.github.io/docs/spot/v1/en/#query-deposit-address

        :param currency: Cryptocurrency
        """
        params = _QueryDepositAddress(
            currency=currency,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/account/deposit/address')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def query_withdraw_quota(self, currency: str) -> Dict:
        """
        Parent user could query withdrawing quota for currencies
        https://huobiapi.github.io/docs/spot/v1/en/#query-withdraw-quota

        :param currency: Cryptocurrency
        """
        params = _QueryWithdrawQuota(
            currency=currency,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/account/withdraw/quota')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def query_withdraw_address(
            self,
            currency: str,
            chain: Optional[str] = None,
            note: Optional[str] = None,
            limit: int = 100,
            from_id: Optional[int] = None,
    ) -> Dict:
        """
        This endpoint allows parent user to query withdraw address available for API key
        https://huobiapi.github.io/docs/spot/v1/en/#query-withdraw-quota

        :param currency: Cryptocurrency
        :param chain: Block chain name
        :param note: The note of withdraw address
        :param limit: The number of items to return
        :param from_id: First record ID in this query
        """
        if limit < 1 or limit > 500:
            raise ValueError(f'Wrong limit value "{limit}"')
        params = _QueryWithdrawAddress(
            currency=currency,
            chain=chain,
            note=note,
            limit=limit,
            fromId=from_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/account/withdraw/address')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def create_withdraw_request(
            self,
            address: str,
            currency: str,
            amount: float,
            fee: Optional[float] = None,
            chain: Optional[str] = None,
            addr_tag: Optional[str] = None,
            client_order_id: Optional[str] = None,
    ) -> Dict:
        """
        Parent user creates a withdraw request from spot account to an external address (exists in
        your withdraw address list), which doesn't require two-factor-authentication
        https://huobiapi.github.io/docs/spot/v1/en/#create-a-withdraw-request

        :param address: The desination address of this withdraw
        :param currency: Cryptocurrency
        :param amount: The amount of currency to withdraw
        :param fee: Fee
        :param chain: Refer to GET /v2/reference/currencies
        :param addr_tag: A tag specified for this address
        :param client_order_id: Client order id
        """
        params = _CreateWithdrawRequest(
            address=address,
            currency=currency,
            amount=amount,
            fee=fee,
            chain=chain,
            addr_tag=addr_tag,
            client_order_id=client_order_id,
        )
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/dw/withdraw/api/create')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(by_alias=True, exclude_none=True),
        )

    async def query_withdrawal_order_by_client_order_id(self, client_order_id: str) -> Dict:
        """
        Query withdrawal order by client order id
        https://huobiapi.github.io/docs/spot/v1/en/#query-withdrawal-order-by-client-order-id

        :param client_order_id: Client order id
        """
        params = _QueryWithdrawalOrderByClientOrderId(
            clientOrderId=client_order_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/query/withdraw/client-order-id')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def cancel_withdraw_request(self, withdraw_id: int) -> Dict:
        """
        Parent user cancels a previously created withdrawal request by its transfer id
        https://huobiapi.github.io/docs/spot/v1/en/#cancel-a-withdraw-request

        :param withdraw_id: The id returned when previously created a withdraw request
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/dw/withdraw-virtual/{withdraw_id}/cancel')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
        )

    async def search_for_existed_withraws_and_deposits(
            self,
            transfer_type: str,
            currency: Optional[str] = None,
            from_transfer_id: Optional[str] = None,
            size: int = 100,
            direct: Direct = Direct.prev,
    ) -> Dict:
        """
        Parent user and sub user search for all existed withdraws and deposits and return their latest status
        https://huobiapi.github.io/docs/spot/v1/en/#search-for-existed-withdraws-and-deposits

        :param transfer_type: Define transfer type to search (deposit, withdraw, sub user can only use deposit)
        :param currency: The cryptocurrency to withdraw
        :param from_transfer_id: The transfer id to begin search
        :param size: The number of items to return
        :param direct: The order of response ('prev' (ascending), 'next' (descending))
        """
        if size < 1 or size > 500:
            raise ValueError(f'Wrong size value "{size}"')
        params = _SearchExistedWithdrawsAndDeposits(
            currency=currency,
            transfer_type=transfer_type,
            from_transfer_id=from_transfer_id,
            size=size,
            direct=direct,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/query/deposit-withdraw')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )
