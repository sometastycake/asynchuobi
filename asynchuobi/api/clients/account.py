from typing import Dict, Iterable, Optional
from urllib.parse import urljoin

from asynchuobi.api.schemas import (
    _AssetTransfer,
    _GetAccountHistory,
    _GetAccountLedger,
    _GetPointBalance,
    _GetTotalValuation,
    _GetTotalValuationPlatformAssets,
)
from asynchuobi.api.strategy.abstract import RequestStrategyAbstract
from asynchuobi.api.strategy.request import BaseRequestStrategy
from asynchuobi.auth import APIAuth
from asynchuobi.enums import AccountTypeCode, Sort
from asynchuobi.urls import HUOBI_API_URL


class AccountHuobiClient:

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
        self._requests = request_strategy

    async def __aenter__(self) -> 'AccountHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._requests.close()

    async def accounts(self) -> Dict:
        """
        Get all Accounts of the Current User
        https://huobiapi.github.io/docs/spot/v1/en/#get-all-accounts-of-the-current-user
        """
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
        """
        Get Account Balance of a Specific Account
        https://huobiapi.github.io/docs/spot/v1/en/#get-account-balance-of-a-specific-account

        :param account_id: The specified account id to get balance for,
            can be found by query '/v1/account/accounts' endpoint.
        """
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
        https://huobiapi.github.io/docs/spot/v1/en/#get-the-total-valuation-of-platform-assets

        :param account_type_code: Account type code
        :param valuation_currency: If not filled, the default is BTC
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
        See https://huobiapi.github.io/docs/spot/v1/en/#get-asset-valuation

        :param account_type: Account type
        :param valuation_currency: The valuation according to the certain fiat currency
        :param sub_uid: Sub User's UID
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
        """
        This endpoint allows parent user and sub user to transfer asset between accounts
        https://huobiapi.github.io/docs/spot/v1/en/#asset-transfer

        :param from_user: Transfer out user uid
        :param from_account_type: 	Transfer out account type
        :param from_account: Transfer out account id
        :param to_user: Transfer in user uid
        :param to_account_type: Transfer in account type
        :param to_account: Transfer in account id
        :param currency: Currency name
        :param amount: 	Amount of fund to transfer
        """
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
        """
        This endpoint returns the amount changes of a specified user's account
        https://huobiapi.github.io/docs/spot/v1/en/#get-account-history

        :param account_id: Account id, refer to GET /v1/account/accounts
        :param currency: Currency name
        :param transact_types: Transact types
        :param start_time: The start time of the query window (unix time in millisecond)
        :param end_time: The end time of the query window (unix time in millisecond)
        :param size: Maximum number of items in each response
        :param sorting: Sorting order
        :param from_id: First record ID in this query
        """
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
            sorting=str(sorting.value),
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
        """
        This endpoint returns the amount changes of specified user's account
        https://huobiapi.github.io/docs/spot/v1/en/#get-account-ledger

        :param account_id: Account id
        :param currency: Cryptocurrency
        :param transact_types: Transaction types
        :param start_time: Farthest time
        :param end_time: Nearest time
        :param sorting: Sorting order
        :param limit: Maximum number of items in one page
        :param from_id: First record ID in this quer
        """
        if limit < 1 or limit > 500:
            raise ValueError(f'Wrong limit value "{limit}"')
        params = _GetAccountLedger(
            accountId=account_id,
            currency=currency,
            transactTypes=transact_types,
            startTime=start_time,
            endTime=end_time,
            sorting=str(sorting.value),
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
        """
        Transferring from a spot account to a contract account, the type
        is pro-to-futures; transferring from a contract account to a spot account,
        the type is futures-to-pro
        https://huobiapi.github.io/docs/spot/v1/en/#transfer-fund-between-spot-account-and-future-contract-account

        :param currency: Currency name
        :param amount: Amount of fund to transfer
        :param transfer_type: Type of the transfer
        """
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
        """
        https://huobiapi.github.io/docs/spot/v1/en/#get-point-balance

        :param sub_user_id: Sub user’s UID (only valid for scenario of parent user
            querying sub user’s point balance)
        """
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

    async def point_transfer(
            self,
            from_uid: str,
            to_uid: str,
            group_id: int,
            amount: float,
    ) -> Dict:
        """
        Via this endpoint, parent user should be able to transfer points between parent
        user and sub user, sub user should be able to transfer point to parent user.
        https://huobiapi.github.io/docs/spot/v1/en/#point-transfer

        :param from_uid: Transferer’s UID
        :param to_uid: Transferee’s UID
        :param group_id: Group ID
        :param amount: Transfer amount (precision: maximum 8 decimal places)
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
