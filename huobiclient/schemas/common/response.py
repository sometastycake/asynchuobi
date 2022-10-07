from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from huobiclient.enums import SymbolStatus
from huobiclient.schemas.base import BaseHuobiResponse


class CurrentTimestampResponse(BaseHuobiResponse):
    data: int


class SupportedTradingSymbol(BaseModel):
    symbol_code: str = Field(alias='sc')
    display_name: str = Field(alias='dn')
    base_currency: str = Field(alias='bc')
    base_currency_display_name: str = Field(alias='bcdn')
    quote_currency: str = Field(alias='qc')
    quote_currency_display_name: str = Field(alias='qcdn')
    symbol_status: SymbolStatus = Field(alias='state')
    white_enabled: bool = Field(alias='whe')
    country_disabled: bool = Field(alias='cd')
    trade_enabled: bool = Field(alias='te')
    trade_open_at: int = Field(alias='toa')
    symbol_partition: str = Field(alias='sp')
    weight: int = Field(alias='w')
    trade_total_precision: Decimal = Field(alias='ttp')
    trade_amount_precision: Decimal = Field(alias='tap')
    trade_price_precision: Decimal = Field(alias='tpp')
    fee_precision: Decimal = Field(alias='fp')
    leverage_ratio: Optional[Decimal] = Field(alias='lr')
    super_margin_leverage_ratio: Optional[Decimal] = Field(alias='smlr')
    funding_leverage_ratio: Optional[Decimal] = Field(alias='flr')
    withdraw_risk: Optional[str] = Field(alias='wr')
    direction: Optional[int] = Field(alias='d')
    etp_leverage_ratio: Optional[str] = Field(alias='elr')


class SupportedTradingSymbolsResponse(BaseHuobiResponse):
    data: List[SupportedTradingSymbol]
    timestamp: int = Field(alias='ts')
    full: int
