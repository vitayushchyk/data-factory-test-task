from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import get_async_session
from services.plan_insert_service import PlanService
from services.plan_performance_service import PlanPerformanceService
from services.user_credits_service import UserCreditService
from services.year_rerformance_servise import YearPerformanceService


async def get_plan_insert_service(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[PlanService, None]:
    yield PlanService(session)


async def get_plan_performance_service(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[PlanPerformanceService, None]:
    yield PlanPerformanceService(session)


async def get_year_performance_service(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[YearPerformanceService, None]:
    yield YearPerformanceService(session)


async def get_user_credits_service(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[UserCreditService, None]:
    yield UserCreditService(session)
