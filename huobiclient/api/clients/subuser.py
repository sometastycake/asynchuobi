from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

from huobiclient.api.dto import (
    SubUserCreation,
    _APIKeyQuery,
    _GetAccountBalanceOfSubUser,
    _GetSubUsersAccountList,
    _GetSubUsersList,
    _GetSubUserStatus,
    _QueryDepositAddressOfSubUser,
    _QueryDepositHistoryOfSubUser,
    _SubUserApiKeyCreation,
    _SubUserApiKeyModification,
)
from huobiclient.api.strategy.abstract import RequestStrategyAbstract
from huobiclient.api.strategy.request import BaseRequestStrategy
from huobiclient.auth import APIAuth
from huobiclient.enums import (
    ApiKeyPermission,
    DeductMode,
    LockSubUserAction,
    MarginAccountActivation,
    MarginAccountType,
    Sort,
    TransferTypeBetweenParentAndSubUser,
)
from huobiclient.urls import HUOBI_API_URL


class SubUserHuobiClient:

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        api_url: str = HUOBI_API_URL,
        request_strategy: RequestStrategyAbstract = BaseRequestStrategy(),
    ):
        self._api = api_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._rstrategy = request_strategy
        if not self._access_key or not self._secret_key:
            raise ValueError('Access key or secret key can not be empty')

    async def __aenter__(self) -> 'SubUserHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    async def set_deduction_for_parent_and_sub_user(self, sub_uids: Iterable[int], deduct_mode: DeductMode) -> Dict:
        """
        This interface is to set the deduction fee for parent and sub user (HT or point)
        https://huobiapi.github.io/docs/spot/v1/en/#set-a-deduction-for-parent-and-sub-user

        :param sub_uids: sub user's UID list (maximum 50 UIDs)
        :param deduct_mode: deduct mode
        """
        if not isinstance(sub_uids, Iterable):
            raise TypeError(f'Iterable type expected for sub_uids, got "{type(sub_uids)}"')
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/deduct-mode')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'subUids': ','.join([str(sub_uid) for sub_uid in sub_uids]),
                'deductMode': deduct_mode.value,
            },
        )

    async def api_key_query(self, uid: int, access_key: Optional[str] = None) -> Dict:
        """
        This endpoint is used by the parent user to query their own API key information,
        and the parent user to query their sub user's API key information
        https://huobiapi.github.io/docs/spot/v1/en/#api-key-query

        :param uid: parent user uid , sub user uid
        :param access_key: the access key of the API key, if not specified,
            it will return all API keys belong to the UID.
        """
        params = _APIKeyQuery(
            uid=uid,
            accessKey=access_key,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/user/api-key')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_uid(self) -> Dict:
        """
        This endpoint allow users to view the user ID of the account easily
        https://huobiapi.github.io/docs/spot/v1/en/#get-uid
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/user/uid')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=auth.to_request(url, 'GET'),
        )

    async def sub_user_creation(self, request: SubUserCreation) -> Dict:
        """
        This endpoint is used by the parent user to create sub users, up to 50 at a time
        https://huobiapi.github.io/docs/spot/v1/en/#sub-user-creation
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/creation')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json=request.dict(exclude_none=True),
        )

    async def get_sub_users_list(self, from_id: Optional[int] = None) -> Dict:
        """
        Via this endpoint parent user is able to query a full list of sub
        user's UID as well as their status
        https://huobiapi.github.io/docs/spot/v1/en/#get-sub-user-39-s-list

        :param from_id: First record ID in next page
        """
        params = _GetSubUsersList(
            fromId=from_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/user-list')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def lock_unlock_sub_user(self, sub_uid: int, action: LockSubUserAction) -> Dict:
        """
        This endpoint allows parent user to lock or unlock a specific sub user
        https://huobiapi.github.io/docs/spot/v1/en/#lock-unlock-sub-user

        :param sub_uid: Sub user UID
        :param action: Action type
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/management')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'subUid': sub_uid,
                'action': action.value,
            },
        )

    async def get_sub_user_status(self, sub_uid: int) -> Dict:
        """
        Via this endpoint, parent user is able to query sub user's
        status by specifying a UID
        https://huobiapi.github.io/docs/spot/v1/en/#get-sub-user-39-s-status

        :param sub_uid: Sub user's UID
        """
        params = _GetSubUserStatus(
            subUid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/user-state')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def set_tradable_market_for_sub_users(
            self,
            sub_uids: Iterable[int],
            account_type: MarginAccountType,
            activation: MarginAccountActivation,
    ) -> Dict:
        """
        Parent user is able to set tradable market for a batch of sub users through this
        endpoint. By default, sub user’s trading permission in
        spot market is activated
        https://huobiapi.github.io/docs/spot/v1/en/#set-tradable-market-for-sub-users

        :param sub_uids: Sub user's UID list
        :param account_type: Account type (isolated-margin,cross-margin)
        :param activation: Account activation (activated,deactivated)
        """
        if not isinstance(sub_uids, Iterable):
            raise TypeError(f'Iterable type expected for sub_uids, got "{type(sub_uids)}"')
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/tradable-market')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'subUids': ','.join([str(sub_uid) for sub_uid in sub_uids]),
                'accountType': account_type.value,
                'activation': activation.value,
            },
        )

    async def set_asset_transfer_permission_for_sub_users(
            self,
            sub_uids: Iterable[int],
            transferrable: bool,
            account_type: str = 'spot',
    ) -> Dict:
        """
        Parent user is able to set asset transfer permission for a batch of sub users.
        By default, the asset transfer from sub user’s spot account to
        parent user’s spot account is allowed
        https://huobiapi.github.io/docs/spot/v1/en/#set-asset-transfer-permission-for-sub-users

        :param sub_uids: Sub user's UID list
        :param transferrable: Transferrablility
        :param account_type: Account type
        """
        if not isinstance(sub_uids, Iterable):
            raise TypeError(f'Iterable type expected for sub_uids, got "{type(sub_uids)}"')
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/transferability')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'subUids': ','.join([str(sub_uid) for sub_uid in sub_uids]),
                'accountType': account_type,
                'transferrable': str(transferrable).lower(),
            },
        )

    async def get_sub_users_account_list(self, sub_uid: int) -> Dict:
        """
        Via this endpoint parent user is able to query account list of
        sub user by specifying a UID
        https://huobiapi.github.io/docs/spot/v1/en/#get-sub-user-39-s-account-list

        :param sub_uid: Sub User's UID
        """
        params = _GetSubUsersAccountList(
            subUid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/account-list')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def sub_user_api_key_creation(
            self,
            sub_uid: int,
            note: str,
            permissions: List[ApiKeyPermission],
            ip_addresses: Optional[Iterable[str]] = None,
            otp_token: Optional[str] = None
    ) -> Dict:
        """
        This endpoint is used by the parent user to create the API key of the sub user
        https://huobiapi.github.io/docs/spot/v1/en/#sub-user-api-key-creation

        :param sub_uid: Sub user UID
        :param note: API keynote
        :param permissions: API key permissions
        :param ip_addresses: The IPv4/IPv6 host address or IPv4 network address bound to the API key
        :param otp_token: Google verification code of the parent user, the parent user must be
            bound to Google Authenticator for verification on the web
        """
        if not isinstance(permissions, list):
            raise TypeError(f'List expected for permissions, got "{type(permissions)}"')
        if ip_addresses is not None:
            if not isinstance(ip_addresses, Iterable):
                raise TypeError(f'Iterable type expected for ip addresses, got "{type(ip_addresses)}"')
            addresses = ','.join(ip_addresses)
        else:
            addresses = None
        if ApiKeyPermission.readOnly not in permissions:
            permissions.append(ApiKeyPermission.readOnly)
        params = _SubUserApiKeyCreation(
            otpToken=otp_token,
            subUid=sub_uid,
            note=note,
            permission=','.join([str(perm.value) for perm in permissions]),
            ipAddresses=addresses,
        )
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/api-key-generation')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(exclude_none=True),
        )

    async def sub_user_api_key_modification(
            self,
            sub_uid: int,
            access_key: str,
            note: Optional[str] = None,
            permissions: Optional[Iterable[ApiKeyPermission]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
    ) -> Dict:
        """
        This endpoint is used by the parent user to modify the API key of the sub user
        https://huobiapi.github.io/docs/spot/v1/en/#sub-user-api-key-modification

        :param sub_uid: sub user uid
        :param access_key: Access key for sub user API key
        :param note: API keynote for sub user API key
        :param permissions: API key permission for sub user API key
        :param ip_addresses: At most 20 IPv4/IPv6 host address(es) and/or
            IPv4 network address(es) can bind with one API key
        """
        if ip_addresses is not None:
            if not isinstance(ip_addresses, Iterable):
                raise TypeError(f'Iterable type expected for ip addresses, got "{type(ip_addresses)}"')
            addresses = ','.join(ip_addresses)
        else:
            addresses = None
        if permissions is not None and not isinstance(permissions, Iterable):
            raise TypeError(f'Iterable type expected for permissions, got "{type(permissions)}"')
        params = _SubUserApiKeyModification(
            accessKey=access_key,
            subUid=sub_uid,
            note=note,
            permission=','.join([str(perm.value) for perm in permissions]) if permissions else None,
            ipAddresses=addresses,
        )
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/api-key-modification')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(exclude_none=True),
        )

    async def sub_user_api_key_deletion(self, sub_uid: int, access_key: str) -> Dict:
        """
        This endpoint is used by the parent user to delete the API key of the sub user
        https://huobiapi.github.io/docs/spot/v1/en/#sub-user-api-key-deletion

        :param sub_uid: sub user uid
        :param access_key Access key for sub user API key
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/api-key-deletion')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
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
        This endpoint allows user to transfer asset between parent and subaccount
        https://huobiapi.github.io/docs/spot/v1/en/#transfer-asset-between-parent-and-sub-account

        :param sub_uid: The subaccount's uid to transfer to or from
        :param currency: The type of currency to transfer
        :param amount: The amount of asset to transfer
        :param transfer_type: The type of transfer
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/subuser/transfer')
        return await self._rstrategy.request(
            method='POST',
            url=url,
            params=auth.to_request(url, 'POST'),
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
        https://huobiapi.github.io/docs/spot/v1/en/#query-deposit-address-of-sub-user

        :param sub_uid: Sub user UID
        :param currency: Cryptocurrency
        """
        params = _QueryDepositAddressOfSubUser(
            subUid=sub_uid,
            currency=currency,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/deposit-address')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
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
        https://huobiapi.github.io/docs/spot/v1/en/#query-deposit-history-of-sub-user

        :param sub_uid: Sub user UID
        :param currency: Cryptocurrency (default value: all)
        :param start_time: Farthest time
        :param end_time: Nearest time
        :param sorting: Sorting order
        :param limit: Maximum number of items in one page
        :param from_id: First record ID in this query
        """
        if limit < 1 or limit > 500:
            raise ValueError(f'Wrong limit value "{limit}"')
        params = _QueryDepositHistoryOfSubUser(
            subUid=sub_uid,
            currency=currency,
            startTime=start_time,
            endTime=end_time,
            sorting=str(sorting.value),
            limit=limit,
            fromId=from_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/query-deposit')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_aggregated_balance_of_all_sub_users(self) -> Dict:
        """
        This endpoint returns the aggregated balance from all the sub-users
        https://huobiapi.github.io/docs/spot/v1/en/#get-the-aggregated-balance-of-all-sub-users
        """
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/subuser/aggregate-balance')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=auth.to_request(url, 'GET'),
        )

    async def get_account_balance_of_sub_user(self, sub_uid: int) -> Dict:
        """
        This endpoint returns the balance of a sub-user specified by sub-uid
        https://huobiapi.github.io/docs/spot/v1/en/#get-account-balance-of-a-sub-user

        :param sub_uid: The specified sub user id to get balance for.
        """
        params = _GetAccountBalanceOfSubUser(
            sub_uid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/account/accounts/{sub_uid}')
        return await self._rstrategy.request(
            method='GET',
            url=url,
            params=params.to_request(url, 'GET'),
        )
