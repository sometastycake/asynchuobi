from typing import List, Union

from huobiclient.schemas.ws.market.request import (
    MarketBestBidOfferRequest,
    MarketByPriceRefreshUpdateRequest,
    MarketCandleRequest,
    MarketDetailRequest,
    MarketEtpRealTimeNavRequest,
    MarketOrderbookRequest,
    MarketTickerRequest,
    MarketTradeDetailRequest,
)
from huobiclient.schemas.ws.market.response import (
    MarketBestBidOfferResponse,
    MarketByPriceRefreshUpdateResponse,
    MarketCandleResponse,
    MarketDetailResponse,
    MarketEtpRealTimeNavResponse,
    MarketOrderbookResponse,
    MarketTickerResponse,
    MarketTradeDetailResponse,
)
from huobiclient.ws.client import HuobiMarketWebsocket
from huobiclient.ws.context import (
    _WebsocketContextManager_MarketBestBidOfferResponse,
    _WebsocketContextManager_MarketByPriceRefreshUpdateResponse,
    _WebsocketContextManager_MarketCandleResponse,
    _WebsocketContextManager_MarketDetailResponse,
    _WebsocketContextManager_MarketEtpRealTimeNavResponse,
    _WebsocketContextManager_MarketOrderbookResponse,
    _WebsocketContextManager_MarketTickerResponse,
    _WebsocketContextManager_MarketTradeDetailResponse,
)


def market_ticker_stream(
        request: Union[MarketTickerRequest, List[MarketTickerRequest]],
) -> _WebsocketContextManager_MarketTickerResponse:
    """
    Retrieve the market ticker,data is pushed every 100ms.
    """
    return _WebsocketContextManager_MarketTickerResponse(
        ws=HuobiMarketWebsocket(),
        request=request,
        response=MarketTickerResponse,
    )


def market_candle_stream(
        request: Union[MarketCandleRequest, List[MarketCandleRequest]],
) -> _WebsocketContextManager_MarketCandleResponse:
    """
    This topic sends a new candlestick whenever it is available.
    """
    return _WebsocketContextManager_MarketCandleResponse(
        ws=HuobiMarketWebsocket(),
        request=request,
        response=MarketCandleResponse,
    )


def market_orderbook_stream(
        request: Union[MarketOrderbookRequest, List[MarketOrderbookRequest]],
) -> _WebsocketContextManager_MarketOrderbookResponse:
    """
    This topic sends the latest market by price order book in snapshot mode at 1-second interval.
    """
    return _WebsocketContextManager_MarketOrderbookResponse(
        ws=HuobiMarketWebsocket(),
        request=request,
        response=MarketOrderbookResponse,
    )


def market_stats_stream(
        request: Union[MarketDetailRequest, List[MarketDetailRequest]],
) -> _WebsocketContextManager_MarketDetailResponse:
    """
    This topic sends the latest market stats with 24h summary. It updates in snapshot mode,
    in frequency of no more than 10 times per second.
    """
    return _WebsocketContextManager_MarketDetailResponse(
        ws=HuobiMarketWebsocket(),
        request=request,
        response=MarketDetailResponse,
    )


def market_trade_detail_stream(
        request: Union[MarketTradeDetailRequest, List[MarketTradeDetailRequest]],
) -> _WebsocketContextManager_MarketTradeDetailResponse:
    """
    This topic sends the latest completed trades. It updates in tick by tick mode.
    """
    return _WebsocketContextManager_MarketTradeDetailResponse(
        ws=HuobiMarketWebsocket(),
        request=request,
        response=MarketTradeDetailResponse,
    )


def market_best_bid_offer_stream(
        request: Union[MarketBestBidOfferRequest, List[MarketBestBidOfferRequest]],
) -> _WebsocketContextManager_MarketBestBidOfferResponse:
    """
    User can receive BBO (Best Bid/Offer) update in tick by tick mode.
    """
    return _WebsocketContextManager_MarketBestBidOfferResponse(
        ws=HuobiMarketWebsocket(),
        request=request,
        response=MarketBestBidOfferResponse,
    )


def etp_real_time_nav_stream(
        request: Union[MarketEtpRealTimeNavRequest, List[MarketEtpRealTimeNavRequest]],
) -> _WebsocketContextManager_MarketEtpRealTimeNavResponse:
    return _WebsocketContextManager_MarketEtpRealTimeNavResponse(
        ws=HuobiMarketWebsocket(),
        request=request,
        response=MarketEtpRealTimeNavResponse,
    )


def market_by_price_refresh_update_stream(
        request: Union[MarketByPriceRefreshUpdateRequest, List[MarketByPriceRefreshUpdateRequest]],
) -> _WebsocketContextManager_MarketByPriceRefreshUpdateResponse:
    """
    User could subscribe to this channel to receive refresh update of Market By Price order book.
    The update interval is around 100ms.
    """
    return _WebsocketContextManager_MarketByPriceRefreshUpdateResponse(
        ws=HuobiMarketWebsocket(),
        request=request,
        response=MarketByPriceRefreshUpdateResponse,
    )
