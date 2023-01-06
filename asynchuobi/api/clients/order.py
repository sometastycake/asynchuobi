from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

from asynchuobi.api.request.abstract import RequestStrategyAbstract
from asynchuobi.api.request.strategy import BaseRequestStrategy
from asynchuobi.api.schemas import (
    NewOrder,
    _BatchCancelOpenOrders,
    _CancelOrder,
    _GetAllOpenOrders,
    _GetCurrentFeeRateAppliedToUser,
    _GetOrderDetailByClientOrderId,
    _SearchHistoricalOrdersWithin48Hours,
    _SearchMatchResult,
    _SearchPastOrder,
)
from asynchuobi.auth import APIAuth
from asynchuobi.enums import Direct, OperatorCharacterOfStopPrice, OrderSide, OrderSource, OrderType
from asynchuobi.urls import HUOBI_API_URL


class OrderHuobiClient:

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

    async def __aenter__(self) -> 'OrderHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._requests.close()

    async def new_order(
            self,
            account_id: int,
            symbol: str,
            order_type: OrderType,
            amount: float,
            price: Optional[float] = None,
            source: OrderSource = OrderSource.spot_api,
            client_order_id: Optional[str] = None,
            self_match_prevent: int = 0,
            stop_price: Optional[float] = None,
            operator: Optional[OperatorCharacterOfStopPrice] = None,
    ) -> Dict:
        params = NewOrder(
            account_id=account_id,
            amount=amount,
            client_order_id=client_order_id,
            operator=operator,
            order_type=order_type,
            price=price,
            self_match_prevent=self_match_prevent,
            source=source,
            stop_price=stop_price,
            symbol=symbol,
        )
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/orders/place')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(by_alias=True, exclude_none=True),
        )

    async def place_batch_of_orders(self, orders: List[NewOrder]) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/batch-orders')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=[order.dict(by_alias=True, exclude_none=True) for order in orders],
        )

    async def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict:
        params = _CancelOrder(
            order_id=order_id,
            symbol=symbol,
        )
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/order/orders/{order_id}/submitcancel')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(by_alias=True, exclude_none=True),
        )

    async def cancel_order_by_client_order_id(self, client_order_id: str) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/orders/submitCancelClientOrder')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'client-order-id': client_order_id,
            },
        )

    async def get_all_open_orders(
            self,
            account_id: Optional[int] = None,
            symbol: Optional[str] = None,
            side: Optional[OrderSide] = None,
            start_order_id: Optional[str] = None,
            direct: Optional[Direct] = None,
            size: int = 100,
    ) -> Dict:
        if size < 1 or size > 500:
            raise ValueError(f'Wrong size value "{size}"')
        params = _GetAllOpenOrders(
            account_id=account_id,
            symbol=symbol,
            side=side,
            start_order_id=start_order_id,
            direct=direct,
            size=size,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/openOrders')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def batch_cancel_open_orders(
            self,
            account_id: Optional[int] = None,
            symbols: Optional[Iterable[str]] = None,
            order_types: Optional[Iterable[OrderType]] = None,
            side: Optional[OrderSide] = None,
            size: int = 100,
    ) -> Dict:
        if size < 1 or size > 100:
            raise ValueError(f'Wrong size value "{size}"')
        if symbols is not None and not isinstance(symbols, Iterable):
            raise TypeError(f'Iterable type expected for symbols, got "{type(symbols)}"')
        if order_types is not None:
            if not isinstance(order_types, Iterable):
                raise TypeError(f'Iterable type expected for order types, got "{type(order_types)}"')
            types = ','.join(map(lambda item: item.value, order_types))
        else:
            types = None
        params = _BatchCancelOpenOrders(
            account_id=account_id,
            symbol=','.join(symbols) if symbols else None,
            order_types=types,
            side=side,
            size=size,
        )
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/orders/batchCancelOpenOrders')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(
                by_alias=True,
                exclude_none=True,
            ),
        )

    async def cancel_order_by_ids(
            self,
            order_ids: Optional[List[str]] = None,
            client_order_ids: Optional[List[str]] = None,
    ) -> Dict:
        params = {}

        if order_ids is not None:
            if not isinstance(order_ids, list):
                raise TypeError('order_ids is not list')
            if order_ids:
                params['order-ids'] = order_ids

        if client_order_ids is not None:
            if not isinstance(client_order_ids, list):
                raise TypeError('client_order_ids is not list')
            if client_order_ids:
                params['client-order-ids'] = client_order_ids

        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/orders/batchcancel')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params,
        )

    async def dead_mans_switch(self, timeout: int) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/algo-orders/cancel-all-after')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'timeout': timeout,
            },
        )

    async def get_order_detail(self, order_id: str) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/order/orders/{order_id}')
        return await self._requests.get(
            url=url,
            params=auth.to_request(url, 'GET'),
        )

    async def get_order_detail_by_client_order_id(self, client_order_id: str) -> Dict:
        params = _GetOrderDetailByClientOrderId(
            clientOrderId=client_order_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/orders/getClientOrder')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_match_result_of_order(self, order_id: str) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/order/orders/{order_id}/matchresults')
        return await self._requests.get(
            url=url,
            params=auth.to_request(url, 'GET'),
        )

    async def search_past_orders(
            self,
            symbol: str,
            states: Iterable[str],
            order_types: Optional[Iterable[OrderType]] = None,
            start_time_ms: Optional[int] = None,
            end_time_ms: Optional[int] = None,
            from_order_id: Optional[str] = None,
            size: int = 100,
            direct: Optional[Direct] = None,
    ) -> Dict:
        if size < 1 or size > 100:
            raise ValueError(f'Wrong size value "{size}"')
        if order_types is not None:
            if not isinstance(order_types, Iterable):
                raise TypeError(f'Iterable type expected for order types, got "{type(order_types)}"')
            types = ','.join(map(lambda item: item.value, order_types))
        else:
            types = None
        params = _SearchPastOrder(
            symbol=symbol,
            states=','.join(states) if states else states,
            order_types=types,
            start_time=start_time_ms,
            end_time=end_time_ms,
            from_order_id=from_order_id,
            size=size,
            direct=direct,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/orders')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def search_historical_orders_within_48_hours(
            self,
            symbol: Optional[str] = None,
            start_time_ms: Optional[int] = None,
            end_time_ms: Optional[int] = None,
            direct: Direct = Direct.next,
            size: int = 100,
    ) -> Dict:
        if size < 10 or size > 1000:
            raise ValueError(f'Wrong size value "{size}"')
        params = _SearchHistoricalOrdersWithin48Hours(
            symbol=symbol,
            start_time=start_time_ms,
            end_time=end_time_ms,
            direct=direct,
            size=size,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/history')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def search_match_results(
            self,
            symbol: str,
            order_types: Optional[Iterable[OrderType]] = None,
            start_time_ms: Optional[int] = None,
            end_time_ms: Optional[int] = None,
            from_order_id: Optional[str] = None,
            size: int = 100,
            direct: Direct = Direct.next,
    ) -> Dict:
        if size < 1 or size > 500:
            raise ValueError(f'Wrong size value "{size}"')
        if order_types is not None:
            if not isinstance(order_types, Iterable):
                raise TypeError(f'Iterable type expected for order types, got "{type(order_types)}"')
            types = ','.join(map(lambda item: item.value, order_types))
        else:
            types = None
        params = _SearchMatchResult(
            symbol=symbol,
            order_types=types,
            start_time=start_time_ms,
            end_time=end_time_ms,
            from_order_id=from_order_id,
            size=size,
            direct=direct,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/matchresults')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_current_fee_rate_applied_to_user(self, symbols: Iterable[str]) -> Dict:
        if not isinstance(symbols, Iterable):
            raise TypeError(f'Iterable type expected for symbols, got "{type(symbols)}"')
        params = _GetCurrentFeeRateAppliedToUser(
            symbols=','.join(symbols),
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/reference/transact-fee-rate')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )
