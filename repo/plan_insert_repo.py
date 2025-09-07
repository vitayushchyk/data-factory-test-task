import calendar
from datetime import date
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select, Row, Date, func, and_

from sqlalchemy import select, Row, Date
from sqlalchemy.ext.asyncio import AsyncSession

from db import Plan, Dictionary
from sqlalchemy import tuple_

from db.credits_model import Credit
from db.payments_model import Payment


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

    async def get_actual_sum(
        self, category: str, period_start: date, period_to: date
    ) -> Decimal:

        if category.lower() == "видача":
            credit_q = select(func.coalesce(func.sum(Credit.body), 0)).where(
                and_(
                    Credit.issuance_date >= period_start,
                    Credit.issuance_date <= period_to,
                )
            )
            credit_res = await self.session.execute(credit_q)
            return Decimal(credit_res.scalar() or 0)
        elif category.lower() == "збір":
            payment_q = select(func.coalesce(func.sum(Payment.sum), 0)).where(
                and_(
                    Payment.payment_date >= period_start,
                    Payment.payment_date <= period_to,
                )
            )
            payment_res = await self.session.execute(payment_q)
            return Decimal(payment_res.scalar() or 0)
        return Decimal(0)

    async def get_plans_for_period(self, period: date):
        result = await self.session.execute(
            select(
                Plan.id,
                Plan.period,
                Plan.sum,
                Dictionary.name.label("category"),
                Plan.category_id,
            )
            .join(Dictionary, Plan.category_id == Dictionary.id)
            .where(Plan.period == period.replace(day=1))
        )
        return result.fetchall()
