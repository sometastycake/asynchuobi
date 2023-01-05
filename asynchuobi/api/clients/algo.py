from typing import Dict, Iterable, Optional
from urllib.parse import urljoin

from asynchuobi.api.request.abstract import RequestStrategyAbstract
from asynchuobi.api.request.strategy import BaseRequestStrategy
from asynchuobi.api.schemas import (
    _NewConditionalOrder,
    _QueryConditionalOrder,
    _QueryConditionalOrderHistory,
    _QueryOpenConditionalOrders,
)
from asynchuobi.auth import APIAuth
from asynchuobi.enums import ConditionalOrderType, OrderSide, Sort
from asynchuobi.urls import HUOBI_API_URL


class AlgoHuobiClient:

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

    async def __aenter__(self) -> 'AlgoHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._requests.close()

    async def new_conditional_order(
            self,
            account_id: int,
            symbol: str,
            order_side: OrderSide,
            order_type: ConditionalOrderType,
            client_order_id: str,
            stop_price: float,
            order_price: Optional[float] = None,
            order_size: Optional[float] = None,
            order_value: Optional[float] = None,
            time_in_force: Optional[str] = None,
            trailing_rate: Optional[float] = None,
    ) -> Dict:
        auth = APIAuth(
            SecretKey=self._secret_key,
            AccessKeyId=self._access_key,
        )
        params = _NewConditionalOrder(
            accountId=account_id,
            symbol=symbol,
            orderPrice=order_price,
            orderSide=order_side,
            orderSize=order_size,
            orderValue=order_value,
            timeInForce=time_in_force,
            orderType=order_type,
            clientOrderId=client_order_id,
            stopPrice=stop_price,
            trailingRate=trailing_rate,
        )
        url = urljoin(self._api, '/v2/algo-orders')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(exclude_none=True),
        )

    async def cancel_conditional_orders(self, client_order_ids: Iterable[str]) -> Dict:
        if not isinstance(client_order_ids, Iterable):
            raise TypeError(f'Iterable type expected for client_order_ids, got "{type(client_order_ids)}"')
        auth = APIAuth(
            SecretKey=self._secret_key,
            AccessKeyId=self._access_key,
        )
        url = urljoin(self._api, '/v2/algo-orders/cancellation')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'clientOrderIds': list(client_order_ids),
            },
        )

    async def query_open_conditional_orders(
            self,
            account_id: Optional[int] = None,
            symbol: Optional[str] = None,
            order_side: Optional[OrderSide] = None,
            order_type: Optional[ConditionalOrderType] = None,
            sorting: Sort = Sort.desc,
            limit: int = 100,
            from_id: Optional[int] = None,
    ) -> Dict:
        if limit < 1 or limit > 500:
            raise ValueError(f'Wrong limit value "{limit}"')
        params = _QueryOpenConditionalOrders(
            accountId=account_id,
            symbol=symbol,
            orderSide=order_side,
            orderType=order_type,
            sort=sorting,
            limit=limit,
            fromId=from_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/algo-orders/opening')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def query_conditional_order_history(
            self,
            symbol: str,
            order_status: str,
            account_id: Optional[int] = None,
            order_side: Optional[OrderSide] = None,
            order_type: Optional[ConditionalOrderType] = None,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None,
            sorting: Sort = Sort.desc,
            limit: int = 100,
            from_id: Optional[int] = None,
    ) -> Dict:
        if limit < 1 or limit > 500:
            raise ValueError(f'Wrong limit value "{limit}"')
        if order_status not in ('canceled', 'rejected', 'triggered'):
            raise ValueError(f'Wrong order status "{order_status}"')
        params = _QueryConditionalOrderHistory(
            accountId=account_id,
            symbol=symbol,
            orderSide=order_side,
            orderType=order_type,
            sort=sorting,
            fromId=from_id,
            startTime=start_time,
            endTime=end_time,
            orderStatus=order_status,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/algo-orders/history')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def query_conditional_order(self, client_order_id: str) -> Dict:
        params = _QueryConditionalOrder(
            clientOrderId=client_order_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/algo-orders/specific')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )
