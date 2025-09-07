from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer


class PlanPerformanceResponse(BaseModel):
    period: date
    category: str
    plan_sum: Decimal
    fact_sum: Decimal
    percent: float


class YearPerformanceResponse(BaseModel):
    month: int
    year: int
    issuance_count: int
    plan_issuance_sum: Decimal
    issuance_sum: Decimal
    pct_issuance_plan: float = Field()
    collection_count: int
    plan_collection_sum: Decimal
    collection_sum: Decimal
    pct_collection_plan: float
    pct_issuance_year: float
    pct_collection_year: float

    @field_serializer("pct_issuance_plan")
    def serialize_pct_issuance_plan(self, v: float) -> float:
        return round(v, 2)

    @field_serializer("pct_collection_plan")
    def serialize_pct_collection_plan(self, v: float) -> float:
        return round(v, 2)

    @field_serializer("pct_issuance_year")
    def serialize_pct_issuance_year(self, v: float) -> float:
        return round(v, 2)

    @field_serializer("pct_collection_year")
    def serialize_pct_collection_year(self, v: float) -> float:
        return round(v, 2)
