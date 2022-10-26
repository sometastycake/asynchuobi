from typing import List, Optional

from pydantic import BaseModel, Field

from huobiclient.auth import APIAuth


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
    accountType: Optional[str]
    valuationCurrency: Optional[str]


class _GetTotalValuation(APIAuth):
    accountType: str
    valuationCurrency: Optional[str]
    subUid: Optional[int]


class _AssetTransfer(BaseModel):
    from_user: int = Field(alias='from-user')
    from_account_type: str = Field(alias='from-account-type')
    from_account: int = Field(alias='from-account')
    to_user: int = Field(alias='to-user')
    to_account_type: str = Field(alias='to-account-type')
    to_account: int = Field(alias='to-account')
    currency: str
    amount: str

    class Config:
        allow_population_by_field_name = True


class _GetAccountHistory(APIAuth):
    account_id: str = Field(alias='account-id')
    currency: Optional[str]
    size: int = Field(default=100, ge=1, le=500)
    from_id: Optional[int] = Field(alias='from-id')

    class Config:
        allow_population_by_field_name = True


class _GetPointBalance(APIAuth):
    subUid: Optional[str] = None


class _GetAccountLedger(APIAuth):
    accountId: str
    currency: Optional[str]
    transactTypes: Optional[str]
    startTime: Optional[int]
    endTime: Optional[int]
    sorting: Optional[str] = Field(alias='sort')
    fromId: Optional[int]

    class Config:
        allow_population_by_field_name = True


class _QueryDepositAddress(APIAuth):
    currency: str


class _QueryWithdrawQuota(APIAuth):
    currency: str


class _QueryWithdrawAddress(APIAuth):
    currency: str
    chain: Optional[str]
    note: Optional[str]
    limit: Optional[str]
    fromId: Optional[int]


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
    transfer_type: str = Field(alias='type')
    from_transfer_id: Optional[str] = Field(alias='from')
    size: Optional[str]
    direct: Optional[str]

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
    subUid: int
    currency: str
