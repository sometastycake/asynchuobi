# Unofficial asynchronous python client for Huobi cryptoexchange

[![CI](https://github.com/sometastycake/asynchuobi/actions/workflows/ci.yml/badge.svg)](https://github.com/sometastycake/asynchuobi/actions/workflows/ci.yml)
[![Python: versions](
https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)]()

## Install

```bash
pip install asynchuobi
```

## Generic API

```python
from asynchuobi.api.clients.generic import GenericHuobiClient


async def main():
    async with GenericHuobiClient() as client:
        current_timestamp = await client.get_current_timestamp()
        trading_symbols = await client.get_all_supported_trading_symbols()
        chains = await client.get_chains_information_v2()
        system_status = await client.get_system_status()
```

## Market API

```python
from asynchuobi.api.clients.market import MarketHuobiClient
from asynchuobi.enums import CandleInterval


async def main():
    async with MarketHuobiClient() as client:
        candles = await client.get_candles('btcusdt', CandleInterval.min_1)
        orderbook = await client.get_market_depth('btcusdt')
        summary = await client.get_last_market_summary('btcusdt')
        recent_trades = await client.get_most_recent_trades('btcusdt')
```

## Subuser API

```python
from asynchuobi.api.clients.subuser import SubUserHuobiClient
from asynchuobi.enums import ApiKeyPermission


async def main():
    async with SubUserHuobiClient(
        access_key='access_key',
        secret_key='secret_key',
    ) as client:
        subusers = await client.get_sub_users_list()
        for subuser in subusers['data']:
            keys = await client.api_key_query(subuser['uid'])
            status = await client.get_sub_user_status(subuser['uid'])
            sub_user_accounts = await client.get_sub_users_account_list(subuser['uid'])
            deposit_address = await client.query_deposit_address_of_sub_user(subuser['uid'], 'usdt')
            deposit_history = await client.query_deposit_history_of_sub_user(subuser['uid'])
            balance = await client.get_account_balance_of_sub_user(subuser['uid'])
            api_key = await client.sub_user_api_key_creation(
                sub_uid=subuser['uid'],
                note='Test api',
                permissions=[ApiKeyPermission.readOnly, ApiKeyPermission.trade],
            )
            api_key_deletion = await client.sub_user_api_key_deletion(
                sub_uid=subuser['uid'],
                access_key=api_key['data']['accessKey'],
            )
```

## Wallet API

```python
from asynchuobi.api.clients.wallet import WalletHuobiClient


async def main():
    async with WalletHuobiClient(
        access_key='access_key',
        secret_key='secret_key',
    ) as client:
        deposit_address = await client.query_deposit_address('usdt')
        withdraw_address = await client.query_withdraw_address('usdt')
        withdraw_quota = await client.query_withdraw_quota('usdt')
        withdraw_response = await client.create_withdraw_request(
            address='address',
            currency='usdt',
            amount=10
        )
```

## Account API

```python
from asynchuobi.api.clients.account import AccountHuobiClient
from asynchuobi.enums import AccountTypeCode, Sort


async def main():
    async with AccountHuobiClient(
        access_key='access_key',
        secret_key='secret_key',
    ) as client:
        accounts = await client.accounts()
        for account in accounts['data']:
            balances = await client.account_balance(account_id=account['id'])
            history = await client.get_account_history(
                account_id=account['id'],
                currency='usdt',
                transact_types=['deposit', 'withdraw'],
                sorting=Sort.desc,
            )

        for account_type in (AccountTypeCode.spot, AccountTypeCode.flat):
            total_valuation = await client.get_total_valuation_of_platform_assets(
                account_type_code=account_type,
                valuation_currency='BTC',
            )
```

## Orders API

```python
from asynchuobi.api.clients.order import OrderHuobiClient
from asynchuobi.enums import OrderType

async def main():
    async with OrderHuobiClient(
            access_key='access_key',
            secret_key='secret_key'
    ) as client:
        response = await client.new_order(
            account_id=account_id,
            symbol='dogeusdt',
            order_type=OrderType.buy_limit,
            amount=20,
            price=0.0660,
        )
        if response['status'] == 'ok':
            # Cancel order
            order_id = response['data']
            cancelling = await client.cancel_order(
                order_id=order_id,
            )
    
        active_orders = await client.get_all_open_orders()
        order_detail = await client.get_order_detail_by_client_order_id(
            client_order_id=client_order_id,
        )
```


## WebSocket

Client supports retrieving information about market data, such as candles, orderbook, trade details.

### Usage

```python
from asynchuobi.enums import CandleInterval, MarketDepthAggregationLevel
from asynchuobi.ws.enums import Subcription
from asynchuobi.ws.ws_client import HuobiMarketWebsocket


async def main():
    async with HuobiMarketWebsocket() as ws:
        # Retrieving a new candlestick whenever it is available
        await ws.candlestick('ethusdt', CandleInterval.min_1, Subcription.sub)

        # Retrieving the latest market stats with 24h summary.
        # It updates in snapshot mode, in frequency of no more than 10 times per second
        await ws.market_detail('ethusdt', Subcription.sub)

        # Retrieving the market ticker, data is pushed every 100ms
        await ws.ticker_info('ethusdt', Subcription.sub)

        # Retrieving the latest market by price order book in snapshot mode at 1-second interval
        await ws.orderbook('ethusdt', Subcription.sub, MarketDepthAggregationLevel.step0)

        async for message in ws:
            ...
```

You can define callbacks which will called when message was received from websocket

```python
from asynchuobi.ws.enums import Subcription
from asynchuobi.ws.ws_client import HuobiMarketWebsocket


async def main():
    def callback_market_detail(message: dict):
        print(message)

    async with HuobiMarketWebsocket() as ws:
        await ws.market_detail(
            symbol='ethusdt',
            action=Subcription.sub,
            callback=callback_market_detail,
        )
        await ws.run_with_callbacks()
```

You can also define async callback

### Retrieving information about account balance changing and about orders

Authentication is required

```python
from asynchuobi.ws.ws_client import HuobiAccountWebsocket


async def main():
    async with HuobiAccountWebsocket(
            access_key='access_key',
            secret_key='secret_key',
    ) as ws:
        # The topic updates account change details.
        await ws.subscribe_account_change()

        # Retrieving information about order cancelling, order creating, order matching
        await ws.subscribe_order_updates('btcusdt')

        async for message in ws:
            ...
```

With callbacks

```python
from asynchuobi.ws.ws_client import HuobiAccountWebsocket


async def main():
    def callback_balance_update(message: dict):
        print(message)

    async with HuobiAccountWebsocket(
            access_key='access_key',
            secret_key='secret_key',
    ) as ws:
        await ws.subscribe_account_change(
            callback=callback_balance_update,
        )
        await ws.run_with_callbacks()
```