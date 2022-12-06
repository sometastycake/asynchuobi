# Unofficial asynchronous python client for Huobi cryptoexchange

[![CI](https://github.com/sometastycake/asynchuobi/actions/workflows/ci.yml/badge.svg)](https://github.com/sometastycake/asynchuobi/actions/workflows/ci.yml)
[![Python: versions](
https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)]()

## Install

```bash
pip install asynchuobi
```

## WebSocket

Client supports retrieving information about market data, such as candles, orderbook, trade details.

### Usage


```python
async with HuobiMarketWebsocket() as ws:
    await ws.market_candlestick_stream('btcusdt', CandleInterval.min_1, SubUnsub.sub)
    await ws.market_detail_stream('ethusdt', SubUnsub.sub)
    async for message in ws:
        ...
```

You can define callbacks which will called when message was received from websocket

```python
def callback_market_detail(message: dict):
    print(message)

async with HuobiMarketWebsocket() as ws:
    await ws.market_detail_stream(
        symbol='ethusdt',
        action=SubUnsub.sub,
        callback=callback_market_detail,
    )
    await ws.run_with_callbacks()
```

You can also define async callback

### Retrieving information about account balance changing and about orders

Authentication is required

```python
async with HuobiAccountWebsocket(
    access_key='access_key',
    secret_key='secret_key',
) as ws:
    await ws.subscribe_account_change()
    await ws.subscribe_order_updates('btcusdt')
    async for message in ws:
        ...
```

With callbacks

```python
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