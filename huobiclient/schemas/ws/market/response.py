from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from huobiclient.enums import TradeDirection


class Candle(BaseModel):
    open: Decimal = Field(description='Opening price during the interval')
    close: Decimal = Field(description='Closing price during the interval')
    low: Decimal = Field(description='Low price during the interval')
    high: Decimal = Field(description='High price during the interval')
    amount: Decimal = Field(description='Aggregated trading volume during the interval (in base currency)')
    vol: Decimal = Field(description='Aggregated trading value during the interval (in quote currency)')
    count: int = Field(description='Number of trades during the interval')


class MarketCandle(Candle):
    tick_id: int = Field(alias='id')


class MarketCandleResponse(BaseModel):
    ch: str
    ts: int
    tick: MarketCandle


class MarketTicker(Candle):
    bid: Decimal = Field(description='Best bid price')
    bid_size: Decimal = Field(description='Best bid size', alias='bidSize')
    ask: Decimal = Field(description='Best ask price')
    ask_size: Decimal = Field(description='Best ask size', alias='askSize')
    last_price: Decimal = Field(description='Last traded price', alias='lastPrice')
    last_size: Decimal = Field(description='Last traded size', alias='lastSize')


class MarketTickerResponse(BaseModel):
    ch: str
    ts: int
    tick: MarketTicker


class MarketOrderbook(BaseModel):
    bids: List[List[Decimal]]
    asks: List[List[Decimal]]


class MarketOrderbookResponse(BaseModel):
    ch: str
    ts: int
    tick: MarketOrderbook


class MarketDetailResponse(MarketCandleResponse):
    ...


class MarketTradeDetail(BaseModel):
    trade_id: int = Field(alias='tradeId')
    amount: Decimal
    price: Decimal
    direction: TradeDirection
    ts: int


class MarketTradeDetailTick(BaseModel):
    global_transaction_id: int = Field(alias='id')
    ts: int
    data: List[MarketTradeDetail]


class MarketTradeDetailResponse(BaseModel):
    ch: str
    ts: int
    tick: MarketTradeDetailTick


class MarketBestBidOffer(BaseModel):
    seq_id: int = Field(alias='seqId')
    ask: Decimal
    ask_size: Decimal = Field(alias='askSize')
    bid: Decimal
    bidSize: Decimal
    quote_time: int = Field(alias='quoteTime')
    symbol: str


class MarketBestBidOfferResponse(BaseModel):
    ch: str
    ts: int
    tick: MarketBestBidOffer


class MarketEtpRealTimeNavBasket(BaseModel):
    amount: Decimal
    currency: str


class MarketEtpRealTimeNavTick(BaseModel):
    actual_leverage: Decimal = Field(alias='actualLeverage')
    nav: Decimal
    outstanding: Decimal
    symbol: str
    nav_time: int = Field(alias='navTime')
    basket: List[MarketEtpRealTimeNavBasket]


class MarketEtpRealTimeNavResponse(BaseModel):
    ch: str
    ts: int
    status: str
    tick: MarketEtpRealTimeNavTick
