from datetime import date
from typing import Dict, Iterable, Optional, Union
from urllib.parse import urljoin

from asynchuobi.api.request.abstract import RequestStrategyAbstract
from asynchuobi.api.request.strategy import BaseRequestStrategy
from asynchuobi.api.schemas import (
    _GetBalanceOfCrossMarginLoanAccount,
    _GetBalanceOfMarginLoanAccount,
    _GetLoanInterestRateAndQuota,
    _RepaymentRecordReference,
    _SearchPastCrossMarginOrders,
    _SearchPastIsolatedMarginOrders,
)
from asynchuobi.auth import APIAuth
from asynchuobi.enums import Direct, Sort
from asynchuobi.urls import HUOBI_API_URL


class MarginHuobiClient:

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

    async def __aenter__(self) -> 'MarginHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._requests.close()

    async def repay_margin_loan(
            self,
            account_id: int,
            currency: str,
            amount: float,
            transact_id: Optional[str] = None,
    ) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/account/repayment')
        params = dict(
            accountid=account_id,
            currency=currency,
            amount=amount,
        )
        if transact_id is not None:
            params['transactId'] = transact_id
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params,
        )

    async def transfer_asset_from_spot_to_isolated_margin_account(
            self,
            symbol: str,
            currency: str,
            amount: float,
    ) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/dw/transfer-in/margin')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=dict(
                symbol=symbol,
                currency=currency,
                amount=amount,
            ),
        )

    async def transfer_asset_from_isolated_margin_account_to_spot(
            self,
            symbol: str,
            currency: str,
            amount: float,
    ) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/dw/transfer-out/margin')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=dict(
                symbol=symbol,
                currency=currency,
                amount=amount,
            ),
        )

    async def get_isolated_loan_interest_rate_and_quota(
            self,
            symbols: Optional[Iterable[str]] = None,
    ) -> Dict:
        if symbols and not isinstance(symbols, Iterable):
            raise TypeError(f'Iterable type expected for symbols, got "{type(symbols)}"')
        params = _GetLoanInterestRateAndQuota(
            symbols=','.join(symbols) if symbols else None,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/margin/loan-info')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def request_isolated_margin_loan(
            self,
            symbol: str,
            currency: str,
            amount: float,
    ) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/margin/orders')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=dict(
                symbol=symbol,
                currency=currency,
                amount=amount,
            ),
        )

    async def repay_isolated_margin_loan(self, amount: float, loan_order_id: str) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/margin/orders/{loan_order_id}/repay')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=dict(
                amount=amount,
            ),
        )

    async def search_past_isolated_margin_orders(
            self,
            symbol: str,
            states: Optional[Iterable[str]] = None,
            start_date: Optional[Union[str, date]] = None,
            end_date: Optional[Union[str, date]] = None,
            from_order_id: Optional[str] = None,
            direct: Optional[Direct] = None,
            size: int = 100,
            sub_uid: Optional[int] = None,
    ) -> Dict:
        if states and not isinstance(states, Iterable):
            raise TypeError(f'Iterable type expected for states, got "{type(states)}"')
        for dt in (start_date, end_date):
            if dt and not isinstance(dt, (str, date)):
                raise TypeError(f'Wrong date value "{dt}"')
        params = _SearchPastIsolatedMarginOrders(
            symbol=symbol,
            states=','.join(states) if states else None,
            start_date=str(start_date) if start_date else None,
            end_date=str(end_date) if end_date else None,
            from_order_id=from_order_id,
            direct=direct,
            size=size,
            sub_uid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/margin/loan-orders')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_balance_of_isolated_margin_account(
            self,
            symbol: Optional[str] = None,
            sub_uid: Optional[str] = None,
    ) -> Dict:
        params = _GetBalanceOfMarginLoanAccount(
            symbol=symbol,
            sub_uid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/margin/accounts/balance')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def transfer_asset_from_spot_to_cross_margin_account(
            self,
            currency: str,
            amount: float,
    ) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/cross-margin/transfer-in')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=dict(currency=currency, amount=amount),
        )

    async def transfer_asset_from_cross_margin_to_spot_account(
            self,
            currency: str,
            amount: float,
    ) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/cross-margin/transfer-out')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=dict(currency=currency, amount=amount),
        )

    async def get_cross_loan_interest_rate_and_quota(self) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/cross-margin/loan-info')
        return await self._requests.get(
            url=url,
            params=auth.to_request(url, 'GET'),
        )

    async def request_cross_margin_loan(self, currency: str, amount: float) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/cross-margin/orders')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=dict(currency=currency, amount=amount),
        )

    async def repay_cross_margin_loan(self, loan_order_id: str, amount: float) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/cross-margin/orders/{loan_order_id}/repay')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=dict(amount=amount),
        )

    async def search_past_cross_margin_orders(
            self,
            currency: Optional[str] = None,
            state: Optional[str] = None,
            start_date: Optional[Union[str, date]] = None,
            end_date: Optional[Union[str, date]] = None,
            from_order_id: Optional[str] = None,
            direct: Optional[Direct] = None,
            size: int = 10,
            sub_uid: Optional[int] = None,
    ) -> Dict:
        if size < 10 or size > 100:
            raise ValueError(f'Wrong size value "{size}"')
        for dt in (start_date, end_date):
            if dt and not isinstance(dt, (str, date)):
                raise TypeError(f'Wrong date value "{dt}"')
        params = _SearchPastCrossMarginOrders(
            currency=currency,
            state=state,
            start_date=str(start_date) if start_date else None,
            end_date=str(end_date) if end_date else None,
            from_order_id=from_order_id,
            direct=direct,
            size=size,
            sub_uid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/cross-margin/loan-orders')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_balance_of_cross_margin_account(
            self,
            sub_uid: Optional[int] = None,
    ) -> Dict:
        params = _GetBalanceOfCrossMarginLoanAccount(
            sub_uid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/cross-margin/accounts/balance')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def repayment_record_reference(
            self,
            repay_id: Optional[int] = None,
            account_id: Optional[int] = None,
            currency: Optional[str] = None,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None,
            sorting: Sort = Sort.desc,
            limit: int = 50,
            from_id: Optional[int] = None,
    ) -> Dict:
        if limit < 1 or limit > 100:
            raise ValueError(f'Wrong limit value "{limit}"')
        params = _RepaymentRecordReference(
            repayId=repay_id,
            accountId=account_id,
            currency=currency,
            startTime=start_time,
            endTime=end_time,
            sorting=sorting,
            limit=limit,
            fromId=from_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/account/repayment')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )
