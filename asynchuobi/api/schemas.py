from typing import List, Optional

from pydantic import BaseModel, Field, StrictInt, StrictStr

from asynchuobi.auth import APIAuth
from asynchuobi.enums import (
    ConditionalOrderType,
    Direct,
    OperatorCharacterOfStopPrice,
    OrderSide,
    OrderSource,
    OrderType,
    Sort,
)


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
    amount: float
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
    amount: float
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
    direct: Direct
    from_transfer_id: Optional[str] = Field(alias='from')
    size: int
    transfer_type: str = Field(alias='type')

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


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


class NewOrder(BaseModel):
    account_id: int = Field(alias='account-id')
    amount: float
    client_order_id: Optional[str] = Field(None, alias='client-order-id')
    operator: Optional[OperatorCharacterOfStopPrice] = None
    order_type: OrderType = Field(alias='type')
    price: Optional[float] = None
    self_match_prevent: int = Field(default=0, alias='self-match-prevent')
    source: OrderSource = OrderSource.spot_api
    stop_price: Optional[float] = Field(None, alias='stop-price')
    symbol: str

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class _CancelOrder(BaseModel):
    order_id: str = Field(alias='order-id')
    symbol: Optional[str]

    class Config:
        allow_population_by_field_name = True


class _GetAllOpenOrders(APIAuth):
    account_id: Optional[int] = Field(None, alias='account-id')
    direct: Optional[Direct]
    side: Optional[str]
    size: int
    start_order_id: Optional[str] = Field(alias='from')
    symbol: Optional[str]

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


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
    direct: Optional[Direct]
    end_time: Optional[int] = Field(None, alias='end-time')
    from_order_id: Optional[str] = Field(None, alias='from')
    size: int
    start_time: Optional[int] = Field(None, alias='start-time')
    states: str
    symbol: str
    order_types: Optional[str] = Field(None, alias='types')

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class _SearchHistoricalOrdersWithin48Hours(APIAuth):
    direct: Direct
    end_time: Optional[int] = Field(None, alias='end-time')
    size: int
    start_time: Optional[int] = Field(None, alias='start-time')
    symbol: Optional[str]

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class _SearchMatchResult(APIAuth):
    direct: Direct
    end_time: Optional[int] = Field(None, alias='end-time')
    from_order_id: Optional[str] = Field(None, alias='from')
    size: int
    start_time: Optional[int] = Field(None, alias='start-time')
    symbol: str
    order_types: Optional[str] = Field(None, alias='types')

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class _GetCurrentFeeRateAppliedToUser(APIAuth):
    symbols: str


class _NewConditionalOrder(BaseModel):
    accountId: int
    symbol: str
    orderPrice: Optional[float]
    orderSide: OrderSide
    orderSize: Optional[float]
    orderValue: Optional[float]
    timeInForce: Optional[str]
    orderType: ConditionalOrderType
    clientOrderId: str
    stopPrice: float
    trailingRate: Optional[float]

    class Config:
        use_enum_values = True


class _QueryOpenConditionalOrders(APIAuth):
    accountId: Optional[int]
    symbol: Optional[str]
    orderSide: Optional[OrderSide]
    orderType: Optional[ConditionalOrderType]
    sorting: Sort = Field(default=Sort.desc, alias='sort')
    limit: int = 100
    fromId: Optional[int]

    class Config:
        use_enum_values = True


class _QueryConditionalOrderHistory(APIAuth):
    accountId: Optional[int]
    symbol: str
    orderSide: Optional[OrderSide]
    orderType: Optional[ConditionalOrderType]
    sorting: Sort = Field(default=Sort.desc, alias='sort')
    limit: int = 100
    fromId: Optional[int]
    orderStatus: str
    startTime: Optional[int]
    endTime: Optional[int]

    class Config:
        use_enum_values = True


class _QueryConditionalOrder(APIAuth):
    clientOrderId: str


class _GetLoanInterestRateAndQuota(APIAuth):
    symbols: Optional[str]


class _SearchPastIsolatedMarginOrders(APIAuth):
    direct: Optional[Direct]
    end_date: Optional[StrictStr] = Field(alias='end-date')
    from_order_id: Optional[str] = Field(alias='from')
    size: int = Field(ge=1, le=100)
    start_date: Optional[StrictStr] = Field(alias='start-date')
    states: Optional[StrictStr]
    sub_uid: Optional[int] = Field(alias='sub-uid')
    symbol: StrictStr

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True


class _GetBalanceOfMarginLoanAccount(APIAuth):
    symbol: Optional[str]
    sub_uid: Optional[int] = Field(alias='sub-uid')

    class Config:
        allow_population_by_field_name = True


class _SearchPastCrossMarginOrders(APIAuth):
    currency: Optional[StrictStr]
    direct: Optional[Direct]
    end_date: Optional[StrictStr] = Field(alias='end-date')
    from_order_id: Optional[str] = Field(alias='from')
    size: StrictInt = 10
    start_date: Optional[StrictStr] = Field(alias='start-date')
    state: Optional[StrictStr]
    sub_uid: Optional[int] = Field(alias='sub-uid')

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True


class _GetBalanceOfCrossMarginLoanAccount(APIAuth):
    sub_uid: Optional[int] = Field(alias='sub-uid')

    class Config:
        allow_population_by_field_name = True


class _RepaymentRecordReference(APIAuth):
    accountId: Optional[int]
    currency: Optional[StrictStr]
    endTime: Optional[StrictInt]
    fromId: Optional[StrictInt]
    limit: StrictInt = 50
    repayId: Optional[int]
    sorting: Sort = Field(Sort.desc, alias='sort')
    startTime: Optional[StrictInt]

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
