from typing import Dict, Iterable, Optional
from urllib.parse import urljoin

from asynchuobi.api.request.abstract import RequestStrategyAbstract
from asynchuobi.api.request.strategy import BaseRequestStrategy
from asynchuobi.api.schemas import (
    _AssetTransfer,
    _GetAccountHistory,
    _GetAccountLedger,
    _GetPointBalance,
    _GetTotalValuation,
    _GetTotalValuationPlatformAssets,
)
from asynchuobi.auth import APIAuth
from asynchuobi.enums import AccountTypeCode, Sort
from asynchuobi.urls import HUOBI_API_URL


class AccountHuobiClient:

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

    async def __aenter__(self) -> 'AccountHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._requests.close()

    async def accounts(self) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/account/accounts')
        return await self._requests.get(
            url=url,
            params=auth.to_request(url, 'GET'),
        )

    async def account_balance(self, account_id: int) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/account/accounts/{account_id}/balance')
        return await self._requests.get(
            url=url,
            params=auth.to_request(url, 'GET'),
        )

    async def get_total_valuation_of_platform_assets(
            self,
            account_type_code: Optional[AccountTypeCode] = None,
            valuation_currency: str = 'BTC',
    ) -> Dict:
        """
        Obtain the total asset valuation of the platform account according
        to the BTC or legal currency denominated unit
        """
        params = _GetTotalValuationPlatformAssets(
            accountType=account_type_code.value if account_type_code else None,
            valuationCurrency=valuation_currency,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/account/valuation')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_asset_valuation(
            self,
            account_type: str,
            valuation_currency: Optional[str] = None,
            sub_uid: Optional[int] = None,
    ) -> Dict:
        """
        This endpoint returns the valuation of the total assets of
        the account in btc or fiat currency
        """
        params = _GetTotalValuation(
            accountType=account_type,
            valuationCurrency=valuation_currency.upper() if valuation_currency else None,
            subUid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/account/asset-valuation')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def asset_transfer(
            self,
            from_user: int,
            from_account_type: str,
            from_account: int,
            to_user: int,
            to_account_type: str,
            to_account: int,
            currency: str,
            amount: float,
    ) -> Dict:
        params = _AssetTransfer(
            from_user=from_user,
            from_account_type=from_account_type,
            from_account=from_account,
            to_user=to_user,
            to_account_type=to_account_type,
            to_account=to_account,
            currency=currency,
            amount=amount,
        )
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/account/transfer')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(by_alias=True),
        )

    async def get_account_history(
            self,
            account_id: int,
            currency: Optional[str] = None,
            transact_types: Optional[Iterable[str]] = None,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None,
            size: int = 100,
            sorting: Sort = Sort.asc,
            from_id: Optional[int] = None,
    ) -> Dict:
        if transact_types is not None:
            if not isinstance(transact_types, Iterable):
                raise TypeError(f'Iterable type expected for transact types, got "{type(transact_types)}"')
            types = ','.join(map(lambda item: item, transact_types))
        else:
            types = None
        if size < 1 or size > 500:
            raise ValueError(f'Wrong size value "{size}"')
        params = _GetAccountHistory(
            account_id=account_id,
            currency=currency,
            size=size,
            transact_types=types,
            start_time=start_time,
            end_time=end_time,
            sorting=sorting,
            from_id=from_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/account/history')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_account_ledger(
            self,
            account_id: int,
            currency: Optional[str] = None,
            transact_types: Optional[str] = None,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None,
            sorting: Sort = Sort.asc,
            limit: int = 100,
            from_id: Optional[int] = None,
    ):
        if limit < 1 or limit > 500:
            raise ValueError(f'Wrong limit value "{limit}"')
        params = _GetAccountLedger(
            accountId=account_id,
            currency=currency,
            transactTypes=transact_types,
            startTime=start_time,
            endTime=end_time,
            sorting=sorting,
            fromId=from_id,
            limit=limit,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/account/ledger')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def transfer_fund_between_spot_and_futures(
            self,
            currency: str,
            amount: float,
            transfer_type: str,
    ) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/futures/transfer')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'currency': currency,
                'amount': amount,
                'type': transfer_type,
            },
        )

    async def get_point_balance(self, sub_user_id: Optional[str] = None) -> Dict:
        params = _GetPointBalance(
            subUid=sub_user_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/point/account')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def point_transfer(self, from_uid: str, to_uid: str, group_id: int, amount: float) -> Dict:
        """
        Via this endpoint, parent user should be able to transfer points between parent
        user and sub user, sub user should be able to transfer point to parent user.
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/point/transfer')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'fromUid': from_uid,
                'toUid': to_uid,
                'groupId': group_id,
                'amount': amount,
            },
        )
