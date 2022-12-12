from datetime import datetime

import pytest
from freezegun import freeze_time

from asynchuobi.ws.ws_client import WSHuobiMarket
from tests.keys import HUOBI_ACCESS_KEY, HUOBI_SECRET_KEY

try:
    from unittest.mock import AsyncMock
except ImportError:
    from mock.mock import AsyncMock

from asynchuobi.api.clients.account import AccountHuobiClient
from asynchuobi.api.clients.generic import GenericHuobiClient
from asynchuobi.api.clients.market import MarketHuobiClient
from asynchuobi.api.clients.order import OrderHuobiClient
from asynchuobi.api.clients.subuser import SubUserHuobiClient
from asynchuobi.api.clients.wallet import WalletHuobiClient
from asynchuobi.auth import APIAuth, WebsocketAuth


@pytest.fixture
def generic_client():
    return GenericHuobiClient(
        request_strategy=AsyncMock(),
    )


@pytest.fixture
def market_client():
    return MarketHuobiClient(
        request_strategy=AsyncMock(),
    )


@pytest.fixture
def account_client():
    return AccountHuobiClient(
        access_key=HUOBI_ACCESS_KEY,
        secret_key=HUOBI_SECRET_KEY,
        request_strategy=AsyncMock(),
    )


@pytest.fixture
def order_client():
    return OrderHuobiClient(
        access_key=HUOBI_ACCESS_KEY,
        secret_key=HUOBI_SECRET_KEY,
        request_strategy=AsyncMock(),
    )


@pytest.fixture
def wallet_client():
    return WalletHuobiClient(
        access_key=HUOBI_ACCESS_KEY,
        secret_key=HUOBI_SECRET_KEY,
        request_strategy=AsyncMock(),
    )


@pytest.fixture
def subuser_client():
    return SubUserHuobiClient(
        access_key=HUOBI_ACCESS_KEY,
        secret_key=HUOBI_SECRET_KEY,
        request_strategy=AsyncMock(),
    )


@pytest.fixture(scope='session')
def api_auth():
    class Data(APIAuth):
        param: str

    with freeze_time(datetime(2023, 1, 1, 0, 1, 1)):
        return Data(
            param='param',
            AccessKeyId=HUOBI_ACCESS_KEY,
            SecretKey=HUOBI_SECRET_KEY,
        )


@pytest.fixture(scope='session')
def ws_auth():
    class Data(WebsocketAuth):
        param: str

    with freeze_time(datetime(2023, 1, 1, 0, 1, 1)):
        return Data(
            param='param',
            accessKey=HUOBI_ACCESS_KEY,
            SecretKey=HUOBI_SECRET_KEY,
        )


@pytest.fixture(scope='function')
def market_websocket():
    return WSHuobiMarket(
        connection=AsyncMock,
    )
