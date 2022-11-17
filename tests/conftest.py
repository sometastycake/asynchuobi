from unittest.mock import AsyncMock

import pytest

from huobiclient.api.clients.account import AccountHuobiClient
from huobiclient.api.clients.generic import GenericHuobiClient
from huobiclient.api.clients.market import MarketHuobiClient
from huobiclient.api.clients.order import OrderHuobiClient
from huobiclient.api.clients.wallet import WalletHuobiClient


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
        access_key='HUOBI_ACCESS_KEY',
        secret_key='HUOBI_SECRET_KEY',
        request_strategy=AsyncMock(),
    )


@pytest.fixture
def order_client():
    return OrderHuobiClient(
        access_key='HUOBI_ACCESS_KEY',
        secret_key='HUOBI_SECRET_KEY',
        request_strategy=AsyncMock(),
    )


@pytest.fixture
def wallet_client():
    return WalletHuobiClient(
        access_key='HUOBI_ACCESS_KEY',
        secret_key='HUOBI_SECRET_KEY',
        request_strategy=AsyncMock(),
    )
