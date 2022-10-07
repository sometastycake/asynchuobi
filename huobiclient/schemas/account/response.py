from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from huobiclient.schemas.base import BaseHuobiResponse


class Account(BaseModel):
    account_id: int = Field(alias='id')
    account_type: str = Field(alias='type')
    subtype: str
    state: str


class AccountsResponse(BaseHuobiResponse):
    data: List[Account]


class AccountBalance(BaseModel):
    currency: str
    balance_type: str = Field(alias='type')
    balance: Decimal
    seq_num: int = Field(alias='seq-num')


class AccountBalanceData(BaseModel):
    account_id: int = Field(alias='id')
    account_type: str = Field(alias='type')
    state: str
    balances: List[AccountBalance] = Field(alias='list')


class AccountBalanceResponse(BaseHuobiResponse):
    data: AccountBalanceData
