from typing import List, Optional

from pydantic import BaseModel, Field

from huobiclient.auth import APIAuth
from huobiclient.enums import OrderSource


class _GetChainsInformationRequest(BaseModel):
    show_desc: Optional[int] = Field(default=None, alias='show-desc')
    ts: Optional[int] = None
    currency: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class _GetMarketSymbolsSettings(BaseModel):
    ts: Optional[int] = None
    symbols: Optional[str] = None


class _GetTotalValuationPlatformAssets(APIAuth):
    accountType: Optional[int]
    valuationCurrency: Optional[str]


class _GetTotalValuation(APIAuth):
    accountType: str
    subUid: Optional[int]
    valuationCurrency: Optional[str]


class _AssetTransfer(BaseModel):
    amount: str
    currency: str
    from_account: int = Field(alias='from-account')
    from_account_type: str = Field(alias='from-account-type')
    from_user: int = Field(alias='from-user')
    to_account: int = Field(alias='to-account')
    to_account_type: str = Field(alias='to-account-type')
    to_user: int = Field(alias='to-user')

    class Config:
        allow_population_by_field_name = True


class _GetAccountHistory(APIAuth):
    account_id: int = Field(alias='account-id')
    currency: Optional[str]
    end_time: Optional[int] = Field(alias='end-time')
    from_id: Optional[int] = Field(alias='from-id')
    size: int = 100
    sorting: str = Field(alias='sort', default='asc')
    start_time: Optional[int] = Field(alias='start-time')
    transact_types: Optional[str] = Field(alias='transact-types')

    class Config:
        allow_population_by_field_name = True


class _GetPointBalance(APIAuth):
    subUid: Optional[str] = None


class _GetAccountLedger(APIAuth):
    accountId: int
    currency: Optional[str]
    endTime: Optional[int]
    fromId: Optional[int]
    limit: int = 100
    sorting: str = Field(alias='sort', default='asc')
    startTime: Optional[int]
    transactTypes: Optional[str]

    class Config:
        allow_population_by_field_name = True


class _QueryDepositAddress(APIAuth):
    currency: str


class _QueryWithdrawQuota(APIAuth):
    currency: str


class _QueryWithdrawAddress(APIAuth):
    chain: Optional[str]
    currency: str
    fromId: Optional[int]
    limit: int
    note: Optional[str]


class _CreateWithdrawRequest(BaseModel):
    address: str
    currency: str
    amount: str
    fee: Optional[float] = None
    chain: Optional[str] = None
    addr_tag: Optional[str] = Field(default=None, alias='addr-tag')
    client_order_id: Optional[str] = Field(default=None, alias='client-order-id')

    class Config:
        allow_population_by_field_name = True


class _QueryWithdrawalOrderByClientOrderId(APIAuth):
    clientOrderId: str


class _SearchExistedWithdrawsAndDeposits(APIAuth):
    currency: Optional[str]
    direct: str
    from_transfer_id: Optional[str] = Field(alias='from')
    size: int
    transfer_type: str = Field(alias='type')

    class Config:
        allow_population_by_field_name = True


class _APIKeyQuery(APIAuth):
    uid: int
    accessKey: Optional[str]


class SubUser(BaseModel):
    userName: str
    note: Optional[str]


class SubUserCreation(BaseModel):
    userList: List[SubUser]


class _GetSubUsersList(APIAuth):
    fromId: Optional[int]


class _GetSubUserStatus(APIAuth):
    subUid: int


class _GetSubUsersAccountList(APIAuth):
    subUid: int


class _SubUserApiKeyCreation(BaseModel):
    otpToken: Optional[str]
    subUid: int
    note: str
    permission: str
    ipAddresses: Optional[str]


class _SubUserApiKeyModification(BaseModel):
    subUid: int
    accessKey: str
    note: Optional[str]
    permission: Optional[str]
    ipAddresses: Optional[str]


class _QueryDepositAddressOfSubUser(APIAuth):
    currency: str
    subUid: int


class _QueryDepositHistoryOfSubUser(APIAuth):
    currency: Optional[str]
    endTime: Optional[int]
    fromId: Optional[int]
    limit: int = 100
    sorting: str = Field(alias='sort', default='asc')
    startTime: Optional[int]
    subUid: int

    class Config:
        allow_population_by_field_name = True


class _GetAccountBalanceOfSubUser(APIAuth):
    sub_uid: int = Field(alias='sub-uid')

    class Config:
        allow_population_by_field_name = True


class PlaceNewOrder(BaseModel):
    account_id: int = Field(alias='account-id')
    amount: str
    client_order_id: Optional[str] = Field(None, alias='client-order-id')
    operator: Optional[str] = None
    order_type: str = Field(alias='type')
    price: Optional[str] = None
    self_match_prevent: int = Field(default=0, alias='self-match-prevent')
    source: str = OrderSource.spot_api.value
    stop_price: Optional[str] = Field(None, alias='stop-price')
    symbol: str

    class Config:
        allow_population_by_field_name = True


class _CancelOrder(BaseModel):
    order_id: str = Field(alias='order-id')
    symbol: Optional[str]

    class Config:
        allow_population_by_field_name = True


class _GetAllOpenOrders(APIAuth):
    account_id: Optional[int] = Field(None, alias='account-id')
    direct: Optional[str]
    side: Optional[str]
    size: int
    start_order_id: Optional[str] = Field(alias='from')
    symbol: Optional[str]

    class Config:
        allow_population_by_field_name = True


class _BatchCancelOpenOrders(BaseModel):
    account_id: Optional[str] = Field(None, alias='account-id')
    side: Optional[str] = None
    size: int
    symbol: Optional[str] = None
    order_types: Optional[str] = Field(None, alias='types')

    class Config:
        allow_population_by_field_name = True


class _GetOrderDetailByClientOrderId(APIAuth):
    clientOrderId: str


class _SearchPastOrder(APIAuth):
    direct: Optional[str]
    end_time: Optional[int] = Field(None, alias='end-time')
    from_order_id: Optional[str] = Field(None, alias='from')
    size: int
    start_time: Optional[int] = Field(None, alias='start-time')
    states: str
    symbol: str
    order_types: Optional[str] = Field(None, alias='types')

    class Config:
        allow_population_by_field_name = True


class _SearchHistoricalOrdersWithin48Hours(APIAuth):
    direct: str
    end_time: Optional[int] = Field(None, alias='end-time')
    size: int
    start_time: Optional[int] = Field(None, alias='start-time')
    symbol: Optional[str]

    class Config:
        allow_population_by_field_name = True


class _SearchMatchResult(APIAuth):
    direct: str
    end_time: Optional[int] = Field(None, alias='end-time')
    from_order_id: Optional[str] = Field(None, alias='from')
    size: int
    start_time: Optional[int] = Field(None, alias='start-time')
    symbol: str
    order_types: Optional[str] = Field(None, alias='types')

    class Config:
        allow_population_by_field_name = True


class _GetCurrentFeeRateAppliedToUser(APIAuth):
    symbols: str
