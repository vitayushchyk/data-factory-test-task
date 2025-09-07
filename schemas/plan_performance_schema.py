from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class PlanPerformanceResponse(BaseModel):
    period: date
    category: str
    plan_sum: Decimal
    fact_sum: Decimal
    percent: float
