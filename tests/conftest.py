from unittest.mock import AsyncMock

import pytest

from huobiclient.api.client import HuobiClient
from huobiclient.config import HuobiConfig


@pytest.fixture(scope='function')
def client():
    client = HuobiClient(HuobiConfig(
        HUOBI_ACCESS_KEY='HUOBI_ACCESS_KEY',
        HUOBI_SECRET_KEY='HUOBI_SECRET_KEY',
    ))
    client._session = AsyncMock()
    return client


@pytest.fixture
def cfg(client):
    return client._cfg  # noqa
