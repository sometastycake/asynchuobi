from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

from huobiclient.api.dto import (
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
from huobiclient.api.strategy.abstract import RequestStrategyAbstract
from huobiclient.api.strategy.request import BaseRequestStrategy
from huobiclient.auth import APIAuth
from huobiclient.cfg import HUOBI_ACCESS_KEY, HUOBI_API_URL, HUOBI_SECRET_KEY
from huobiclient.enums import Direct, OperatorCharacterOfStopPrice, OrderSide, OrderSource, OrderType


class OrderHuobiClient:

    def __init__(
        self,
        api_url: str = HUOBI_API_URL,
        access_key: str = HUOBI_ACCESS_KEY,
        secret_key: str = HUOBI_SECRET_KEY,
        request_strategy: RequestStrategyAbstract = BaseRequestStrategy(),
    ):
        self._api = api_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._rstrategy = request_strategy
        if not self._access_key or not self._secret_key:
            raise ValueError('Access key or secret key can not be empty')
    
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
        """
        This endpoint places a new order and sends to the exchange to be matched
        https://huobiapi.github.io/docs/spot/v1/en/#place-a-new-order

        :param account_id: The account id used for this trade
        :param symbol: The trading symbol to trade
        :param order_type: The order type
        :param amount: Order size (for buy market order, it's order value)
        :param price: The order price (not available for market order)
        :param source: When trade with spot use 'spot-api'
        :param client_order_id: Client order ID
        :param self_match_prevent: self match prevent.
            0: no, means allowing self-trading; 1: yes, means not allowing self-trading
        :param stop_price: Trigger price of stop limit order
        :param operator: Operation charactor of stop price
        """
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
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(by_alias=True, exclude_none=True),
        )

    async def place_batch_of_orders(self, orders: List[NewOrder]) -> Dict:
        """
        A batch contains at most 10 orders.
        https://huobiapi.github.io/docs/spot/v1/en/#place-a-batch-of-orders
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/batch-orders')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json=[order.dict(by_alias=True, exclude_none=True) for order in orders],
        )

    async def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict:
        """
        This endpoint submits a request to cancel an order.
        https://huobiapi.github.io/docs/spot/v1/en/#submit-cancel-for-an-order

        :param order_id: The previously returned order id when order was created
        :param symbol: Symbol which needs to be filled in the URL
        """
        params = _CancelOrder(
            order_id=order_id,
            symbol=symbol,
        )
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/order/orders/{order_id}/submitcancel')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(by_alias=True, exclude_none=True),
        )

    async def cancel_order_by_client_order_id(self, client_order_id: str) -> Dict:
        """
        This endpoint submit a request to cancel an order based on client-order-id
        https://huobiapi.github.io/docs/spot/v1/en/#submit-cancel-for-an-order-based-on-client-order-id

        :param client_order_id: Client order ID, it must exist within 8 hours,
            otherwise it is not allowed to use when placing a new order
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/orders/submitCancelClientOrder')
        return await self._rstrategy.request(
            method='POST',
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
        """
        This endpoint returns all open orders which have not been filled completely
        https://huobiapi.github.io/docs/spot/v1/en/#get-all-open-orders

        :param account_id: The account id used for this trade
        :param symbol: The trading symbol to trade
        :param side: Filter on the direction of the trade
        :param start_order_id: Start order ID the searching to begin with
        :param direct: Searching direction
        :param size: The number of orders to return
        """
        if size < 1 or size > 500:
            raise ValueError(f'Wrong size value "{size}"')
        params = _GetAllOpenOrders(
            account_id=account_id,
            symbol=symbol,
            side=side.value if side else None,
            start_order_id=start_order_id,
            direct=direct,
            size=size,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/openOrders')
        return await self._rstrategy.request(
            method='GET',
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
        """
        This endpoint submit cancellation for multiple orders (not exceeding 100 orders
        per request) at once with given criteria
        https://huobiapi.github.io/docs/spot/v1/en/#submit-cancel-for-multiple-orders-by-criteria

        :param account_id: The account id used for this cancel
        :param symbols: The trading symbol list
        :param order_types: One or more types of order to include in the search
        :param side: Filter on the direction of the trade
        :param size: The number of orders to cancel
        """
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
            side=str(side.value) if side else None,
            size=size,
        )
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/orders/batchCancelOpenOrders')
        return await self._rstrategy.request(
            method='POST',
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
        """
        This endpoint submit cancellation for multiple orders at once with given ids.
        It is suggested to use order-ids instead of client-order-ids, so that the cancellation
        is faster, more accurate and more stable
        https://huobiapi.github.io/docs/spot/v1/en/#submit-cancel-for-multiple-orders-by-ids

        :param order_ids: The order ids to cancel
        :param client_order_ids: The client order ids to cancel
        """
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
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params,
        )

    async def dead_mans_switch(self, timeout: int) -> Dict:
        """
        The Dead man’s switch protects the user’s assets when the connection to the exchange is
        lost due to network or system errors
        https://huobiapi.github.io/docs/spot/v1/en/#dead-man-s-switch

        :param timeout: Time out duration (unit：second)
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/algo-orders/cancel-all-after')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'timeout': timeout,
            },
        )

    async def get_order_detail(self, order_id: str) -> Dict:
        """
        This endpoint returns the detail of a specific order. If an order is created via API,
        then it's no longer queryable after being cancelled for 2 hours
        https://huobiapi.github.io/docs/spot/v1/en/#get-the-order-detail-of-an-order

        :param order_id: Order id when order was created
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/order/orders/{order_id}')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=auth.to_request(url, 'GET'),
        )

    async def get_order_detail_by_client_order_id(self, client_order_id: str) -> Dict:
        """
        This endpoint returns the detail of one order by specified client order id (within 8 hours)
        https://huobiapi.github.io/docs/spot/v1/en/#get-the-order-detail-of-an-order-based-on-client-order-id
        """
        params = _GetOrderDetailByClientOrderId(
            clientOrderId=client_order_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/order/orders/getClientOrder')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_match_result_of_order(self, order_id: str) -> Dict:
        """
        This endpoint returns the match result of an order
        https://huobiapi.github.io/docs/spot/v1/en/#get-the-match-result-of-an-order

        :param order_id: Order id
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/order/orders/{order_id}/matchresults')
        return await self._rstrategy.request(
            method='GET',
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
        """
        This endpoint returns orders based on a specific searching criteria. The order created via
        API will no longer be queryable after being cancelled for more than 2 hours
        https://huobiapi.github.io/docs/spot/v1/en/#search-past-orders

        :param symbol: The trading symbol
        :param states: One or more states of order to include in the search
            (filled, partial-canceled, canceled)
        :param order_types: One or more types of order to include in the search
        :param start_time_ms: Search starts time, UTC time in millisecond
        :param end_time_ms: Search ends time, UTC time in millisecond
        :param from_order_id: Search order id to begin with
        :param size: The number of orders to return
        :param direct: Search direction when 'from' is used
        """
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
        return await self._rstrategy.request(
            method='GET',
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
        """
        This endpoint returns orders based on a specific searching criteria
        https://huobiapi.github.io/docs/spot/v1/en/#search-historical-orders-within-48-hours

        :param symbol: The trading symbol to trade
        :param start_time_ms: Start time
        :param end_time_ms: End time
        :param direct: Direction of the query
        :param size: Number of items in each response
        """
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
        return await self._rstrategy.request(
            method='GET',
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
        """
        This endpoint returns the match results of past and current filled, or partially
        filled orders based on specific search criteria
        https://huobiapi.github.io/docs/spot/v1/en/#search-match-results

        :param symbol: The trading symbol to trade
        :param order_types: The types of order to include in the search
        :param start_time_ms: Far point of time of the query window
            (unix time in millisecond)
        :param end_time_ms: Near point of time of the query window
            (unix time in millisecond)
        :param from_order_id: Search internal id to begin with
        :param size: The number of orders to return
        :param direct: Search direction when 'from' is used
        """
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
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_current_fee_rate_applied_to_user(self, symbols: Iterable[str]) -> Dict:
        """
        This endpoint returns the current transaction fee rate applied to the user
        https://huobiapi.github.io/docs/spot/v1/en/#get-current-fee-rate-applied-to-the-user

        :param symbols: The trading symbols to query
        """
        if not isinstance(symbols, Iterable):
            raise TypeError(f'Iterable type expected for symbols, got "{type(symbols)}"')
        params = _GetCurrentFeeRateAppliedToUser(
            symbols=','.join(symbols),
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/reference/transact-fee-rate')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )
