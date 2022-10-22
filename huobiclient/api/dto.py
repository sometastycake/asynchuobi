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
