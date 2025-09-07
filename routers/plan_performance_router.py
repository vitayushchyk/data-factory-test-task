from fastapi import APIRouter, Depends
from datetime import date
from typing import List, Annotated

from starlette import status

from services.plan_performance_service import PlanPerformanceService

from core.deps import get_plan_performance_service

from schemas.plan_performance_schema import PlanPerformanceResponse


plan_perf_rout = APIRouter(tags=["Plan"])


@plan_perf_rout.get(
    "/plans_performance",
    status_code=status.HTTP_200_OK,
    summary="Get plans performance",
    description="Get information about the implementation of plans for a specific date<br>"
    "The target date must be in the format: `YYYY-MM-DD`",
    response_model=List[PlanPerformanceResponse],
)
async def get_plans_performance(
    target_date: date,
    plan_perf_service: Annotated[
        PlanPerformanceService, Depends(get_plan_performance_service)
    ],
):
    return await plan_perf_service.get_performance(target_date)
