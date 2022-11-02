from typing import Any, Dict, List, Optional

import aiohttp
from yarl import URL

from huobiclient.auth import APIAuth
from huobiclient.config import huobi_client_config as config
from huobiclient.enums import (
    ApiKeyPermission,
    CandleInterval,
    DeductMode,
    LockSubUserAction,
    MarketDepthAggregationLevel,
    Sort,
    TransferTypeBetweenParentAndSubUser,
)
from huobiclient.exceptions import HuobiError

from .dto import (
    SubUserCreation,
    _APIKeyQuery,
    _AssetTransfer,
    _CreateWithdrawRequest,
    _GetAccountBalanceOfSubUser,
    _GetAccountHistory,
    _GetAccountLedger,
    _GetChainsInformationRequest,
    _GetMarketSymbolsSettings,
    _GetPointBalance,
    _GetSubUsersAccountList,
    _GetSubUsersList,
    _GetSubUserStatus,
    _GetTotalValuation,
    _GetTotalValuationPlatformAssets,
    _QueryDepositAddress,
    _QueryDepositAddressOfSubUser,
    _QueryDepositHistoryOfSubUser,
    _QueryWithdrawAddress,
    _QueryWithdrawalOrderByClientOrderId,
    _QueryWithdrawQuota,
    _SearchExistedWithdrawsAndDeposits,
    _SubUserApiKeyCreation,
    _SubUserApiKeyModification,
)


class HuobiClient:

    def __init__(self, raise_if_status_error: bool = False):
        self._raise_if_status_error = raise_if_status_error
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
            raise_for_status=True,
        )

    def __del__(self):
        if not self._session.closed:
            self._session.connector.close()

    def _check_error(self, response: Dict) -> None:
        status = response.get('status')
        if isinstance(status, str) and status != 'ok':
            raise HuobiError(
                err_code=response.get('err-code', ''),
                err_msg=response.get('err-msg', ''),
            )

    def _url(self, path: str) -> str:
        return str(URL(config.HUOBI_API_URL).with_path(path))

    async def request(self, path: str, method: str, **kwargs: Any) -> Any:
        """
        Request to Huobi API.
        """
        response = await self._session.request(
            url=self._url(path),
            method=method,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers={
                'Content-Type': 'application/json',
            },
        )
        data = await response.json()
        if self._raise_if_status_error and isinstance(data, dict):
            self._check_error(data)
        return data

    async def get_system_status(self) -> Dict:
        """
        This endpoint allows users to get system status, Incidents and planned maintenance.
        """
        response = await self._session.get(
            url='https://status.huobigroup.com/api/v2/summary.json',
            headers={
                'Content-Type': 'application/json',
            },
        )
        return await response.json()

    async def get_market_status(self) -> Dict:
        """
        The endpoint returns current market status.
        """
        return await self.request(method='GET', path='/v2/market-status')

    async def get_all_supported_trading_symbols(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get all Supported Trading Symbol
        :param timestamp_milliseconds: timestamp to get incremental data
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self.request(
            method='GET',
            path='/v2/settings/common/symbols',
            params=params,
        )

    async def get_all_supported_currencies(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get all Supported Currencies
        :param timestamp_milliseconds: timestamp to get incremental data
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self.request(
            method='GET',
            path='/v2/settings/common/currencies',
            params=params,
        )

    async def get_currencies_settings(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get Currencies Settings
        :param timestamp_milliseconds: timestamp to get incremental data
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self.request(
            method='GET',
            path='/v1/settings/common/currencys',
            params=params,
        )

    async def get_symbols_settings(
            self,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get Symbols Settings
        :param timestamp_milliseconds: timestamp to get incremental data
        """
        params = {}
        if timestamp_milliseconds is not None:
            params['ts'] = timestamp_milliseconds
        return await self.request(
            method='GET',
            path='/v1/settings/common/symbols',
            params=params,
        )

    async def get_market_symbols_settings(
            self,
            symbols: Optional[List[str]] = None,
            timestamp_milliseconds: Optional[int] = None,
    ) -> Dict:
        """
        Get Market Symbols Setting
        :param symbols: symbols
        :param timestamp_milliseconds: timestamp to get incremental data
        """
        params = _GetMarketSymbolsSettings(
            ts=timestamp_milliseconds,
            symbols=','.join(symbols) if isinstance(symbols, list) else symbols,
        )
        return await self.request(
            method='GET',
            path='/v1/settings/common/market-symbols',
            params=params.dict(exclude_none=True),
        )

    async def get_chains_information(
            self,
            show_desc: Optional[int] = None,
            timestamp_milliseconds: Optional[int] = None,
            currency: Optional[str] = None,
    ) -> Dict:
        """
        Get Chains Information
        :param show_desc: show desc, 0: no, 1: all, 2: suspend deposit/withdrawal and chain exchange
        :param timestamp_milliseconds: timestamp to get incremental data
        :param currency: currency
        """
        params = _GetChainsInformationRequest(
            show_desc=show_desc,
            ts=timestamp_milliseconds,
            currency=currency,
        )
        return await self.request(
            method='GET',
            path='/v1/settings/common/chains',
            params=params.dict(by_alias=True, exclude_none=True),
        )

    async def get_chains_information_v2(
            self,
            currency: Optional[str] = None,
            authorized_user: bool = True,
    ) -> Dict:
        """
        API user could query static reference information for each currency,
        as well as its corresponding chain(s)
        """
        params = {
            'authorizedUser': str(authorized_user).lower(),
        }
        if currency is not None:
            params['currency'] = currency.lower()
        return await self.request(
            method='GET',
            path='/v2/reference/currencies',
            params=params,
        )

    async def get_current_timestamp(self) -> Dict:
        """
        This endpoint returns the current timestamp, i.e. the number of
        milliseconds that have elapsed since 00:00:00 UTC on 1 January 1970.
        """
        return await self.request(method='GET', path='/v1/common/timestamp')

    async def get_candles(self, symbol: str, interval: CandleInterval, size: int = 150) -> Dict:
        """
        Market data APIs provide public market information such as varies of candlestick,
        depth and trade information.
        The market data is updated once per second
        :param symbol: The trading symbol to query
        :param interval: The period of each candle
        :param size: The number of data returns
        """
        if size < 1 or size > 2000:
            raise ValueError(f'Wrong size value "{size}"')
        return await self.request(
            method='GET',
            path='/market/history/kline',
            params={
                'symbol': symbol,
                'period': interval.value,
                'size': size,
            },
        )

    async def get_latest_aggregated_ticker(self, symbol: str) -> Dict:
        """
        This endpoint retrieves the latest ticker with some important 24h
        aggregated market data.
        :param symbol: The trading symbol to query
        """
        return await self.request(
            method='GET',
            path='/market/detail/merged',
            params={
                'symbol': symbol,
            },
        )

    async def get_latest_tickers_for_all_pairs(self) -> Dict:
        """
        This endpoint retrieves the latest tickers for all supported pairs.
        """
        return await self.request(method='GET', path='/market/tickers')

    async def get_market_depth(
        self,
        symbol: str,
        depth: int = 20,
        aggregation_level: MarketDepthAggregationLevel = MarketDepthAggregationLevel.step0,
    ):
        """
        This endpoint retrieves the current order book of a specific pair
        :param symbol: The trading symbol to query
        :param depth: The number of market depth to return on each side
        :param aggregation_level: Market depth aggregation level
        """
        if depth not in (5, 10, 20):
            raise ValueError(f'Wrong market depth value "{depth}"')
        return await self.request(
            method='GET',
            path='/market/depth',
            params={
                'symbol': symbol,
                'depth': depth,
                'type': aggregation_level.value,
            },
        )

    async def get_last_trade(self, symbol: str) -> Dict:
        """
        This endpoint retrieves the latest trade with its price,
        volume, and direction
        :param symbol: The trading symbol to query
        """
        return await self.request(
            method='GET',
            path='/market/trade',
            params={
                'symbol': symbol,
            },
        )

    async def get_most_recent_trades(self, symbol: str, size: int = 1) -> Dict:
        """
        This endpoint retrieves the most recent trades with their price,
        volume, and direction
        :param symbol: The trading symbol to query
        :param size: The number of data returns
        """
        if size < 1 or size > 2000:
            raise ValueError(f'Wrong size value "{size}"')
        return await self.request(
            method='GET',
            path='/market/history/trade',
            params={
                'symbol': symbol,
                'size': size,
            },
        )

    async def get_last_market_summary(self, symbol: str) -> Dict:
        """
        This endpoint retrieves the summary of trading in the market
        for the last 24 hours
        :param symbol: The trading symbol to query
        """
        return await self.request(
            method='GET',
            path='/market/detail/',
            params={
                'symbol': symbol,
            },
        )

    async def get_real_time_nav(self, symbol: str) -> Dict:
        """
        This endpoint returns real time NAV for ETP
        :param symbol: ETP trading symbol
        """
        return await self.request(
            method='GET',
            path='/market/etp',
            params={
                'symbol': symbol,
            },
        )

    async def accounts(self) -> Dict:
        """
        Get all Accounts of the Current User.
        """
        path = '/v1/account/accounts'
        return await self.request(
            method='GET',
            path=path,
            params=APIAuth().to_request(path, 'GET'),
        )

    async def account_balance(self, account_id: int) -> Dict:
        """
        Get Account Balance of a Specific Account

        :param account_id: The specified account id to get balance for,
            can be found by query '/v1/account/accounts' endpoint.
        """
        path = f'/v1/account/accounts/{account_id}/balance'
        return await self.request(
            method='GET',
            path=path,
            params=APIAuth().to_request(path, 'GET'),
        )

    async def get_total_valuation_of_platform_assets(
            self,
            account_type_code: Optional[int] = None,
            valuation_currency: Optional[str] = None,
    ) -> Dict:
        """
        Obtain the total asset valuation of the platform account according
        to the BTC or legal currency denominated unit
        :param account_type_code: see
            https://huobiapi.github.io/docs/spot/v1/en/#get-the-total-valuation-of-platform-assets
        :param valuation_currency: If not filled, the default is BTC
        """
        params = _GetTotalValuationPlatformAssets(
            accountType=str(account_type_code) if account_type_code else account_type_code,
            valuationCurrency=valuation_currency.upper() if valuation_currency else valuation_currency,
        )
        path = '/v2/account/valuation'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
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
        :param account_type: See https://huobiapi.github.io/docs/spot/v1/en/#get-asset-valuation
        :param valuation_currency: The valuation according to the certain fiat currency
        :param sub_uid: Sub User's UID
        """
        params = _GetTotalValuation(
            accountType=account_type,
            valuationCurrency=valuation_currency.upper() if valuation_currency else valuation_currency,
            subUid=sub_uid,
        )
        path = '/v2/account/asset-valuation'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
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
            amount: str,
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
        path = '/v1/account/transfer'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json=params.dict(by_alias=True),
        )

    async def get_account_history(
            self,
            account_id: int,
            currency: Optional[str] = None,
            transact_types: Optional[List[str]] = None,
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
        if size < 1 or size > 500:
            raise ValueError(f'Wrong size value "{size}"')
        params = _GetAccountHistory(
            account_id=account_id,
            currency=currency,
            size=size,
            transact_types=','.join(transact_types) if transact_types else transact_types,
            start_time=start_time,
            end_time=end_time,
            sorting=str(sorting.value),
            from_id=from_id,
        )
        path = '/v1/account/history'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
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
            sorting=str(sorting.value),
            fromId=from_id,
            limit=limit,
        )
        path = '/v2/account/ledger'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
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
        """
        path = '/v1/futures/transfer'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json={
                'currency': currency,
                'amount': amount,
                'type': transfer_type,
            }
        )

    async def get_point_balance(self, sub_user_id: Optional[str] = None) -> Dict:
        params = _GetPointBalance(
            subUid=sub_user_id,
        )
        path = '/v2/point/account'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def point_transfer(
            self,
            from_uid: str,
            to_uid: str,
            group_id: int,
            amount: str,
    ) -> Dict:
        path = '/v2/point/transfer'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json={
                'fromUid': from_uid,
                'toUid': to_uid,
                'groupId': group_id,
                'amount': amount,
            },
        )

    async def query_deposit_address(self, currency: str) -> Dict:
        params = _QueryDepositAddress(
            currency=currency,
        )
        path = '/v2/account/deposit/address'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def query_withdraw_quota(self, currency: str) -> Dict:
        params = _QueryWithdrawQuota(
            currency=currency
        )
        path = '/v2/account/withdraw/quota'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def query_withdraw_address(
            self,
            currency: str,
            chain: Optional[str] = None,
            note: Optional[str] = None,
            limit: Optional[str] = None,
            fromId: Optional[int] = None
    ) -> Dict:
        params = _QueryWithdrawAddress(
            currency=currency,
            chain=chain,
            note=note,
            limit=limit,
            fromId=fromId,
        )
        path = '/v2/account/withdraw/address'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def create_withdraw_request(
            self,
            address: str,
            currency: str,
            amount: str,
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
        path = '/v1/dw/withdraw/api/create'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json=params.dict(by_alias=True, exclude_none=True),
        )

    async def query_withdrawal_order_by_client_order_id(self, client_order_id: str) -> Dict:
        params = _QueryWithdrawalOrderByClientOrderId(
            clientOrderId=client_order_id,
        )
        path = '/v1/query/withdraw/client-order-id'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def cancel_withdraw_request(self, withdraw_id: int) -> Dict:
        path = f'/v1/dw/withdraw-virtual/{withdraw_id}/cancel'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
        )

    async def search_for_existed_withraws_and_deposits(
            self,
            transfer_type: str,
            currency: Optional[str] = None,
            from_trasfer_id: Optional[str] = None,
            size: Optional[str] = None,
            direct: Optional[str] = None,
    ) -> Dict:
        params = _SearchExistedWithdrawsAndDeposits(
            currency=currency,
            transfer_type=transfer_type,
            from_transfer_id=from_trasfer_id,
            size=size,
            direct=direct,
        )
        path = '/v1/query/deposit-withdraw'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def set_deduction_for_parent_and_sub_user(self, sub_uids: List[int], deduct_mode: DeductMode) -> Dict:
        """
        This interface is to set the deduction fee for parent and sub user (HT or point)
        :param sub_uids: sub user's UID list (maximum 50 UIDs, separated by comma)
        :param deduct_mode: deduct mode
        """
        path = '/v2/sub-user/deduct-mode'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json={
                'subUids': ','.join([str(sub_uid) for sub_uid in sub_uids]),
                'deductMode': deduct_mode.value,
            },
        )

    async def api_key_query(self, uid: int, access_key: Optional[str] = None) -> Dict:
        """
        This endpoint is used by the parent user to query their own API key information,
        and the parent user to query their sub user's API key information
        :param uid: parent user uid , sub user uid
        :param access_key: the access key of the API key, if not specified,
            it will return all API keys belong to the UID.
        """
        params = _APIKeyQuery(
            uid=uid,
            accessKey=access_key,
        )
        path = '/v2/user/api-key'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def get_uid(self) -> Dict:
        """
        This endpoint allow users to view the user ID of the account easily.
        """
        path = '/v2/user/uid'
        return await self.request(
            method='GET',
            path=path,
            params=APIAuth().to_request(path, 'GET'),
        )

    async def sub_user_creation(self, request: SubUserCreation) -> Dict:
        """
        This endpoint is used by the parent user to create sub users, up to 50 at a time.
        """
        path = '/v2/sub-user/creation'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json=request.dict(exclude_none=True),
        )

    async def get_sub_users_list(self, from_id: Optional[int] = None) -> Dict:
        """
        Via this endpoint parent user is able to query a full list of sub
        user's UID as well as their status.
        """
        params = _GetSubUsersList(
            fromId=from_id,
        )
        path = '/v2/sub-user/user-list'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def lock_unlock_sub_user(self, sub_uid: int, action: LockSubUserAction) -> Dict:
        """
        This endpoint allows parent user to lock or unlock a specific sub user.
        """
        path = '/v2/sub-user/management'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json={
                'subUid': sub_uid,
                'action': action.value,
            },
        )

    async def get_sub_user_status(self, sub_uid: int) -> Dict:
        """
        Via this endpoint, parent user is able to query sub user's
        status by specifying a UID.
        """
        params = _GetSubUserStatus(
            subUid=sub_uid,
        )
        path = '/v2/sub-user/user-state'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def set_tradable_market_for_sub_users(
            self,
            sub_uids: List[str],
            account_type: str,
            activation: str,
    ) -> Dict:
        """
        Parent user is able to set tradable market for a batch of sub users through this
        endpoint. By default, sub user’s trading permission in
        spot market is activated.
        """
        path = '/v2/sub-user/tradable-market'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json={
                'subUids': ','.join(sub_uids),
                'accountType': account_type,
                'activation': activation,
            },
        )

    async def set_asset_transfer_permission_for_sub_users(
            self,
            sub_uids: List[int],
            transferrable: bool,
            account_type: str = 'spot',
    ) -> Dict:
        """
        Parent user is able to set asset transfer permission for a batch of sub users.
        By default, the asset transfer from sub user’s spot account to
        parent user’s spot account is allowed
        :param sub_uids: Sub user's UID list
        :param transferrable: Transferrablility
        :param account_type: Account type
        """
        path = '/v2/sub-user/transferability'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json={
                'subUids': ','.join([str(sub_uid) for sub_uid in sub_uids]),
                'accountType': account_type,
                'transferrable': str(transferrable).lower(),
            },
        )

    async def get_sub_users_account_list(self, sub_uid: int) -> Dict:
        """
        Via this endpoint parent user is able to query account list of
        sub user by specifying a UID.
        :param sub_uid: Sub User's UID
        """
        params = _GetSubUsersAccountList(
            subUid=sub_uid,
        )
        path = '/v2/sub-user/account-list'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def sub_user_api_key_creation(
            self,
            sub_uid: int,
            note: str,
            permissions: List[ApiKeyPermission],
            ip_addresses: Optional[List[str]] = None,
            otp_token: Optional[str] = None
    ) -> Dict:
        """
        This endpoint is used by the parent user to create the API key of the sub user.
        """
        if ApiKeyPermission.readOnly not in permissions:
            permissions.append(ApiKeyPermission.readOnly)
        params = _SubUserApiKeyCreation(
            otpToken=otp_token,
            subUid=sub_uid,
            note=note,
            permission=','.join([str(perm.value) for perm in permissions]),
            ipAddresses=','.join(ip_addresses) if ip_addresses else ip_addresses,
        )
        path = '/v2/sub-user/api-key-generation'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json=params.dict(exclude_none=True),
        )

    async def sub_user_api_key_modification(
            self,
            sub_uid: int,
            access_key: str,
            note: Optional[str] = None,
            permissions: Optional[List[ApiKeyPermission]] = None,
            ip_addresses: Optional[List[str]] = None,
    ) -> Dict:
        """
        This endpoint is used by the parent user to modify the API key of the sub user
        :param sub_uid: sub user uid
        :param access_key: Access key for sub user API key
        :param note: API keynote for sub user API key
        :param permissions: API key permission for sub user API key
        :param ip_addresses: At most 20 IPv4/IPv6 host address(es) and/or
            IPv4 network address(es) can bind with one API key
        """
        params = _SubUserApiKeyModification(
            accessKey=access_key,
            subUid=sub_uid,
            note=note,
            permission=','.join([str(perm.value) for perm in permissions]) if permissions else permissions,
            ipAddresses=','.join(ip_addresses) if ip_addresses else ip_addresses,
        )
        path = '/v2/sub-user/api-key-modification'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json=params.dict(exclude_none=True),
        )

    async def sub_user_api_key_deletion(self, sub_uid: int, access_key: str) -> Dict:
        """
        This endpoint is used by the parent user to delete the API key of the sub user
        :param sub_uid: sub user uid
        :param access_key Access key for sub user API key
        """
        path = '/v2/sub-user/api-key-deletion'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json={
                'subUid': sub_uid,
                'accessKey': access_key,
            },
        )

    async def transfer_asset_between_parent_and_sub_user(
            self,
            sub_uid: int,
            currency: str,
            amount: float,
            transfer_type: TransferTypeBetweenParentAndSubUser,
    ) -> Dict:
        """
        This endpoint allows user to transfer asset between parent and subaccount.
        :param sub_uid: The subaccount's uid to transfer to or from
        :param currency: The type of currency to transfer
        :param amount: The amount of asset to transfer
        :param transfer_type: The type of transfer
        """
        path = '/v1/subuser/transfer'
        return await self.request(
            method='POST',
            path=path,
            params=APIAuth().to_request(path, 'POST'),
            json={
                'sub-uid': sub_uid,
                'currency': currency,
                'amount': amount,
                'type': transfer_type.value,
            },
        )

    async def query_deposit_address_of_sub_user(
            self,
            sub_uid: int,
            currency: str,
    ) -> Dict:
        """
        Parent user could query sub user's deposit address on corresponding chain,
        for a specific cryptocurrency (except IOTA)
        :param sub_uid: Sub user UID
        :param currency: Cryptocurrency
        """
        params = _QueryDepositAddressOfSubUser(
            subUid=sub_uid,
            currency=currency,
        )
        path = '/v2/sub-user/deposit-address'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def query_deposit_history_of_sub_user(
            self,
            sub_uid: int,
            currency: Optional[str] = None,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None,
            sorting: Sort = Sort.asc,
            limit: int = 100,
            from_id: Optional[int] = None,
    ) -> Dict:
        """
        Parent user could query sub user's deposit history via this endpoint
        :param sub_uid: Sub user UID
        :param currency: Cryptocurrency (default value: all)
        :param start_time: Farthest time
        :param end_time: Nearest time
        :param sorting: Sorting order
        :param limit: Maximum number of items in one page
        :param from_id: First record ID in this query
        """
        params = _QueryDepositHistoryOfSubUser(
            subUid=sub_uid,
            currency=currency,
            startTime=start_time,
            endTime=end_time,
            sorting=str(sorting.value),
            limit=limit,
            fromId=from_id,
        )
        path = '/v2/sub-user/query-deposit'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )

    async def get_aggregated_balance_of_all_sub_users(self) -> Dict:
        """
        This endpoint returns the aggregated balance from all the sub-users.
        """
        path = '/v1/subuser/aggregate-balance'
        return await self.request(
            method='GET',
            path=path,
            params=APIAuth().to_request(path, 'GET'),
        )

    async def get_account_balance_of_sub_user(self, sub_uid: int) -> Dict:
        """
        This endpoint returns the balance of a sub-user specified by sub-uid
        :param sub_uid: The specified sub user id to get balance for.
        """
        params = _GetAccountBalanceOfSubUser(
            sub_uid=sub_uid,
        )
        path = f'/v1/account/accounts/{sub_uid}'
        return await self.request(
            method='GET',
            path=path,
            params=params.to_request(path, 'GET'),
        )
