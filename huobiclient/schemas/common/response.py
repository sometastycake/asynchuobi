from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from huobiclient.enums import (
    AssetType,
    ChainType,
    DepositStatus,
    InstrumentStatus,
    MarketHaltReason,
    MarketStatus,
    SymbolStatus,
    WithdrawFeeType,
    WithdrawStatus,
)
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


class ChainInformation(BaseModel):
    addr_deposit_tag: bool = Field(alias='adt')
    address_chain: str = Field(alias='ac')
    addr_oneoff: bool = Field(alias='ao')
    addr_with_tag: bool = Field(alias='awt')
    chain: str
    chain_type: ChainType = Field(alias='ct')
    code: str
    currency: str
    deposit_desc: Optional[str] = Field(alias='deposit-desc')
    deposit_enable: bool = Field(alias='de')
    deposit_min_amount: Decimal = Field(alias='dma')
    deposit_tips_desc: Optional[str] = Field(alias='deposit-tips-desc')
    display_name: str = Field(alias='dn')
    fast_confirms: int = Field(alias='fc')
    fee_type: str = Field(alias='ft')
    is_default: int = Field(alias='default')
    replace_chain_info_desc: Optional[str] = Field(alias='replace-chain-info-desc')
    replace_chain_notification_desc: Optional[str] = Field(alias='replace-chain-notification-desc')
    replace_chain_popup_desc: Optional[str] = Field(alias='replace-chain-popup-desc')
    safe_confirms: int = Field(alias='sc')
    suspend_deposit_announcement: Optional[str] = Field(alias='sda')
    suspend_deposit_desc: Optional[str] = Field(alias='suspend-deposit-desc')
    suspend_withdraw_announcement: Optional[str] = Field(alias='swa')
    suspend_withdraw_desc: Optional[str] = Field(alias='suspend-withdraw-desc')
    visible: bool = Field(alias='v')
    withdraw_desc: Optional[str] = Field(alias='withdraw-desc')
    withdraw_enable: bool = Field(alias='we')
    withdraw_min_amount: Decimal = Field(alias='wma')
    withraw_precision: int = Field(alias='wp')
    full_name: str = Field(alias='fn')
    withdraw_tips_desc: Optional[str] = Field(alias='withdraw-tips-desc')
    suspend_visible_desc: Optional[str] = Field(alias='suspend-visible-desc')


class GetChainsInformationResponse(BaseHuobiResponse):
    data: List[ChainInformation]


class GetChainsInformationV2(BaseModel):
    chain: str = Field(
        description='Chain name',
    )
    display_name: str = Field(
        alias='displayName',
        description='Chain display name',
    )
    base_chain: Optional[str] = Field(
        alias='baseChain',
        description='Base chain name',
    )
    base_chain_protocol: Optional[str] = Field(
        alias='baseChainProtocol',
        description='Base chain protocol',
    )
    is_dynamic: Optional[bool] = Field(
        alias='isDynamic',
        description='Is dynamic fee type or not',
    )
    num_of_confirmations: int = Field(
        alias='numOfConfirmations',
        description='Number of confirmations required for deposit success',
    )
    num_of_fast_confirmations: int = Field(
        alias='numOfFastConfirmations',
        description='Number of confirmations required for quick success',
    )
    min_deposit_amount: Decimal = Field(
        alias='minDepositAmt',
        description='Minimal deposit amount in each request',
    )
    deposit_status: DepositStatus = Field(
        alias='depositStatus',
    )
    min_withdraw_amount: Decimal = Field(
        alias='minWithdrawAmt',
        description='Minimal withdraw amount in each request',
    )
    max_withdraw_amount: Decimal = Field(
        alias='maxWithdrawAmt',
        description='Maximum withdraw amount in each request',
    )
    withdraw_quota_per_day: Decimal = Field(
        alias='withdrawQuotaPerDay',
        description='Maximum withdraw amount in a day (Singapore timezone)',
    )
    withdraw_quota_per_year: Optional[Decimal] = Field(
        alias='withdrawQuotaPerYear',
        description='Maximum withdraw amount in a year',
    )
    withdraw_quota_total: Optional[Decimal] = Field(
        alias='withdrawQuotaTotal',
        description='Maximum withdraw amount in total',
    )
    withdraw_precision: int = Field(
        alias='withdrawPrecision',
        description='Withdraw amount precision',
    )
    withdraw_fee_type: WithdrawFeeType = Field(
        alias='withdrawFeeType',
        description='Type of withdraw fee',
    )
    transact_fee_withdraw: Optional[Decimal] = Field(
        alias='transactFeeWithdraw',
        description='Withdraw fee in each request',
    )
    min_transact_fee_withdraw: Optional[Decimal] = Field(
        alias='minTransactFeeWithdraw',
        description='Minimal withdraw fee in each request',
    )
    max_transact_fee_withdraw: Optional[Decimal] = Field(
        alias='maxTransactFeeWithdraw',
        description='Maximum withdraw fee in each request',
    )
    transact_fee_rate_withdraw: Optional[Decimal] = Field(
        alias='transactFeeRateWithdraw',
        description='Withdraw fee in each request',
    )
    withdraw_status: WithdrawStatus = Field(alias='withdrawStatus')


class GetChainsInformationV2Data(BaseModel):
    currency: str
    instrument_status: InstrumentStatus = Field(alias='instStatus')
    chains: List[GetChainsInformationV2]


class GetChainsInformationV2Response(BaseModel):
    code: int
    message: Optional[str]
    data: List[GetChainsInformationV2Data]
