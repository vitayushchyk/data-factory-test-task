from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import get_async_session
from services.plan_insert_service import PlanService


async def get_plan_insert_service(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[PlanService, None]:
    yield PlanService(session)
