from typing import Sequence


from sqlalchemy import select, Row, Date
from sqlalchemy.ext.asyncio import AsyncSession

from db import Plan
from sqlalchemy import tuple_


class PlanRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_exists(
        self, periods_and_categories: list[tuple[str, int]]
    ) -> Sequence[Row[tuple[Date, int]]]:
        q = select(Plan.period, Plan.category_id).where(
            tuple_(Plan.period, Plan.category_id).in_(periods_and_categories)
        )
        result = await self.session.execute(q)
        duplicates = result.all()
        return duplicates

    async def add_plans(self, plans: list["Plan"]):
        self.session.add_all(plans)
        await self.session.commit()
        return plans
