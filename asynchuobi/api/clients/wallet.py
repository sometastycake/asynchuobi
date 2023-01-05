from typing import Dict, Optional
from urllib.parse import urljoin

from asynchuobi.api.request.abstract import RequestStrategyAbstract
from asynchuobi.api.request.strategy import BaseRequestStrategy
from asynchuobi.api.schemas import (
    _CreateWithdrawRequest,
    _QueryDepositAddress,
    _QueryWithdrawAddress,
    _QueryWithdrawalOrderByClientOrderId,
    _QueryWithdrawQuota,
    _SearchExistedWithdrawsAndDeposits,
)
from asynchuobi.auth import APIAuth
from asynchuobi.enums import Direct
from asynchuobi.urls import HUOBI_API_URL


class WalletHuobiClient:

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        api_url: str = HUOBI_API_URL,
        requests: Optional[RequestStrategyAbstract] = None,
    ):
        if not access_key or not secret_key:
            raise ValueError('Access key or secret key can not be empty')
        self._api = api_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._requests = requests if requests is not None else BaseRequestStrategy()

    async def __aenter__(self) -> 'WalletHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._requests.close()

    async def query_deposit_address(self, currency: str) -> Dict:
        params = _QueryDepositAddress(
            currency=currency,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/account/deposit/address')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def query_withdraw_quota(self, currency: str) -> Dict:
        params = _QueryWithdrawQuota(
            currency=currency,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/account/withdraw/quota')
        return await self._requests.get(
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
        return await self._requests.get(
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
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(by_alias=True, exclude_none=True),
        )

    async def query_withdrawal_order_by_client_order_id(self, client_order_id: str) -> Dict:
        params = _QueryWithdrawalOrderByClientOrderId(
            clientOrderId=client_order_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/query/withdraw/client-order-id')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def cancel_withdraw_request(self, withdraw_id: int) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/dw/withdraw-virtual/{withdraw_id}/cancel')
        return await self._requests.post(
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
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )
