from typing import Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class CreditInfo(BaseModel):
    credit_id: int
    issuance_date: date
    closed: bool

    actual_return_date: Optional[date]
    body: Decimal
    percent: Decimal
    total_payments: Optional[Decimal]

    return_date: Optional[date]
    days_overdue: Optional[int]
    body_payments: Optional[Decimal]
    percent_payments: Optional[Decimal]


class UserCreditsRes(BaseModel):
    user_id: int
    credits: list[CreditInfo]
