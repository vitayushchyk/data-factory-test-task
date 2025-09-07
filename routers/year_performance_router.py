from typing import Annotated

from fastapi import APIRouter, Depends


from core.deps import get_year_performance_service


from schemas.plan_performance_schema import YearPerformanceResponse


year_performance_router = APIRouter(tags=["Plan"])


@year_performance_router.get(
    "/year_performance",
    summary="Get year performance by year",
    response_model=list[YearPerformanceResponse],
    description="Get information about the performance of plans for a specific year<br>"
    "The target year must be in the format: `YYYY`",
)
async def get_year_performance(
    target_year: int,
    year_perf_service: Annotated[
        YearPerformanceResponse, Depends(get_year_performance_service)
    ],
    limit: int = 12,
    offset: int = 0,
):
    return await year_perf_service.get_year_performance(
        target_year, limit=limit, offset=offset
    )
