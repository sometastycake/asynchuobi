from typing import Optional

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


class _TransferFundBetweenSpotAndFutures(BaseModel):
    currency: str
    amount: float
    transfer_type: str = Field(alias='type')

    class Config:
        allow_population_by_field_name = True


class _PointTransfer(BaseModel):
    fromUid: str
    toUid: str
    groupId: int
    amount: str
