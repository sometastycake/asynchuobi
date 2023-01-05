from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

from asynchuobi.api.request.abstract import RequestStrategyAbstract
from asynchuobi.api.request.strategy import BaseRequestStrategy
from asynchuobi.api.schemas import (
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
from asynchuobi.auth import APIAuth
from asynchuobi.enums import (
    ApiKeyPermission,
    DeductMode,
    LockSubUserAction,
    MarginAccountActivation,
    MarginAccountType,
    Sort,
    TransferTypeBetweenParentAndSubUser,
)
from asynchuobi.urls import HUOBI_API_URL


class SubUserHuobiClient:

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

    async def __aenter__(self) -> 'SubUserHuobiClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # noqa:U100
        await self._requests.close()

    async def set_deduction_for_parent_and_sub_user(self, sub_uids: Iterable[int], deduct_mode: DeductMode) -> Dict:
        if not isinstance(sub_uids, Iterable):
            raise TypeError(f'Iterable type expected for sub_uids, got "{type(sub_uids)}"')
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/deduct-mode')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'subUids': ','.join([str(sub_uid) for sub_uid in sub_uids]),
                'deductMode': deduct_mode.value,
            },
        )

    async def api_key_query(self, uid: int, access_key: Optional[str] = None) -> Dict:
        params = _APIKeyQuery(
            uid=uid,
            accessKey=access_key,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/user/api-key')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_uid(self) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/user/uid')
        return await self._requests.get(
            url=url,
            params=auth.to_request(url, 'GET'),
        )

    async def sub_user_creation(self, request: SubUserCreation) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/creation')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=request.dict(exclude_none=True),
        )

    async def get_sub_users_list(self, from_id: Optional[int] = None) -> Dict:
        params = _GetSubUsersList(
            fromId=from_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/user-list')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def lock_unlock_sub_user(self, sub_uid: int, action: LockSubUserAction) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/management')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'subUid': sub_uid,
                'action': action.value,
            },
        )

    async def get_sub_user_status(self, sub_uid: int) -> Dict:
        params = _GetSubUserStatus(
            subUid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/user-state')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def set_tradable_market_for_sub_users(
            self,
            sub_uids: Iterable[int],
            account_type: MarginAccountType,
            activation: MarginAccountActivation,
    ) -> Dict:
        if not isinstance(sub_uids, Iterable):
            raise TypeError(f'Iterable type expected for sub_uids, got "{type(sub_uids)}"')
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/tradable-market')
        return await self._requests.post(
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
        if not isinstance(sub_uids, Iterable):
            raise TypeError(f'Iterable type expected for sub_uids, got "{type(sub_uids)}"')
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/transferability')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'subUids': ','.join([str(sub_uid) for sub_uid in sub_uids]),
                'accountType': account_type,
                'transferrable': str(transferrable).lower(),
            },
        )

    async def get_sub_users_account_list(self, sub_uid: int) -> Dict:
        params = _GetSubUsersAccountList(
            subUid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/account-list')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def sub_user_api_key_creation(
            self,
            sub_uid: int,
            note: str,
            permissions: List[ApiKeyPermission],
            ip_addresses: Optional[Iterable[str]] = None,
            otp_token: Optional[str] = None,
    ) -> Dict:
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
        return await self._requests.post(
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
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json=params.dict(exclude_none=True),
        )

    async def sub_user_api_key_deletion(self, sub_uid: int, access_key: str) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/api-key-deletion')
        return await self._requests.post(
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
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/subuser/transfer')
        return await self._requests.post(
            url=url,
            params=auth.to_request(url, 'POST'),
            json={
                'sub-uid': sub_uid,
                'currency': currency,
                'amount': amount,
                'type': transfer_type.value,
            },
        )

    async def query_deposit_address_of_sub_user(self, sub_uid: int, currency: str) -> Dict:
        params = _QueryDepositAddressOfSubUser(
            subUid=sub_uid,
            currency=currency,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/deposit-address')
        return await self._requests.get(
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
        if limit < 1 or limit > 500:
            raise ValueError(f'Wrong limit value "{limit}"')
        params = _QueryDepositHistoryOfSubUser(
            subUid=sub_uid,
            currency=currency,
            startTime=start_time,
            endTime=end_time,
            sorting=sorting,
            limit=limit,
            fromId=from_id,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v2/sub-user/query-deposit')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )

    async def get_aggregated_balance_of_all_sub_users(self) -> Dict:
        auth = APIAuth(
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, '/v1/subuser/aggregate-balance')
        return await self._requests.get(
            url=url,
            params=auth.to_request(url, 'GET'),
        )

    async def get_account_balance_of_sub_user(self, sub_uid: int) -> Dict:
        params = _GetAccountBalanceOfSubUser(
            sub_uid=sub_uid,
            AccessKeyId=self._access_key,
            SecretKey=self._secret_key,
        )
        url = urljoin(self._api, f'/v1/account/accounts/{sub_uid}')
        return await self._requests.get(
            url=url,
            params=params.to_request(url, 'GET'),
        )
