from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict

from pydantic import BaseModel, Field

from huobiclient.enums import AssetType, MarketHaltReason, MarketStatus, SymbolStatus
from huobiclient.schemas.base import BaseHuobiResponse


class MarketStatusData(BaseModel):
    marketStatus: MarketStatus
    haltStartTime: Optional[int]
    haltEndTime: Optional[int]
    haltReason: Optional[MarketHaltReason]
    affectedSymbols: Optional[str]


class MarketStatusResponse(BaseModel):
    code: int
    message: Optional[str]
    data: MarketStatusData


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


class SupportedCurrencies(BaseModel):
    currency_code: str = Field(alias='cc')
    display_name: str = Field(alias='dn')
    full_name: str = Field(alias='fn')
    asset_type: AssetType = Field(alias='at')
    withdraw_precision: int = Field(alias='wp')
    fee_type: str = Field(alias='ft')
    deposit_min_amount: Decimal = Field(alias='dma')
    withdraw_min_amount: Decimal = Field(alias='wma')
    show_precision: int = Field(alias='sp')
    weight: int = Field(alias='w')
    quote_currency: bool = Field(alias='qc')
    state: SymbolStatus
    visible: bool = Field(alias='v')
    white_enabled: bool = Field(alias='whe')
    country_disabled: bool = Field(alias='cd')
    deposit_enabled: bool = Field(alias='de')
    withdraw_enabled: bool = Field(alias='wed')
    currency_addr_with_tag: bool = Field(alias='cawt')
    fast_confirms: int = Field(alias='fc')
    safe_confirms: int = Field(alias='sc')
    suspend_withdraw_desc: Optional[str] = Field(alias='swd')
    withdraw_desc: Optional[str] = Field(alias='wd')
    suspend_deposit_desc: Optional[str] = Field(alias='sdd')
    deposit_desc: Optional[str] = Field(alias='dd')
    suspend_visible_desc: Optional[str] = Field(alias='svd')
    tags: str


class SupportedCurrenciesResponse(BaseHuobiResponse):
    data: List[SupportedCurrencies]
    timestamp: int = Field(alias='ts')
    full: int


class SystemStatusPage(BaseModel):
    system_status_page_id: str = Field(alias='id')
    name: str
    url: str
    time_zone: str
    updated_at: datetime


class SystemStatusComponent(BaseModel):
    component_id: str = Field(alias='id')
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    position: int
    description: Optional[str]
    showcase: bool
    start_date: Optional[datetime]
    group_id: Optional[str]
    page_id: Optional[str]
    group: bool
    only_show_if_degraded: bool


class SystemStatusResponse(BaseModel):
    page: SystemStatusPage
    components: List[SystemStatusComponent]
    incidents: List[Dict]
    scheduled_maintenances: List[Dict]
