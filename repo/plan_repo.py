from datetime import date
from decimal import Decimal
from typing import Sequence

from sqlalchemy import func, and_


from sqlalchemy import select, Row, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

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

    async def get_stats(self, year: int, limit: int = 12, offset: int = 0):
        credits_subq = (
            select(
                func.extract("month", Credit.issuance_date).label("month"),
                func.extract("year", Credit.issuance_date).label("year"),
                func.count(Credit.id).label("issuance_count"),
                func.sum(Credit.body).label("issuance_sum"),
            )
            .where(func.extract("year", Credit.issuance_date) == year)
            .group_by("month", "year")
            .subquery()
        )
        year_credits_subq = (
            select(
                func.extract("year", Credit.issuance_date).label("year"),
                func.sum(Credit.body).label("issuance_sum"),
            )
            .where(func.extract("year", Credit.issuance_date) == year)
            .group_by("year")
            .subquery()
        )
        pay_subq = (
            select(
                func.extract("month", Payment.payment_date).label("month"),
                func.extract("year", Payment.payment_date).label("year"),
                func.count(Payment.id).label("collection_count"),
                func.sum(Payment.sum).label("collection_sum"),
            )
            .where(func.extract("year", Payment.payment_date) == year)
            .group_by("month", "year")
            .subquery()
        )
        year_pay_subq = (
            select(
                func.extract("year", Payment.payment_date).label("year"),
                func.sum(Payment.sum).label("collection_sum"),
            )
            .where(func.extract("year", Payment.payment_date) == year)
            .group_by("year")
            .subquery()
        )

        PlanCat3 = aliased(Plan)
        PlanCat4 = aliased(Plan)

        q = (
            select(
                credits_subq.c.month,
                credits_subq.c.year,
                credits_subq.c.issuance_count,
                credits_subq.c.issuance_sum,
                pay_subq.c.collection_count,
                pay_subq.c.collection_sum,
                func.coalesce(PlanCat3.sum, 0).label("plan_issuance_sum"),
                func.coalesce(PlanCat4.sum, 0).label("plan_collection_sum"),
                (
                    (func.coalesce(PlanCat3.sum, 0) / credits_subq.c.issuance_sum) * 100
                ).label("pct_issuance_plan"),
                (
                    (func.coalesce(PlanCat4.sum, 0) / pay_subq.c.collection_sum) * 100
                ).label("pct_collection_plan"),
                (
                    (
                        func.coalesce(credits_subq.c.issuance_sum, 0)
                        / year_credits_subq.c.issuance_sum
                    )
                    * 100
                ).label("pct_issuance_year"),
                (
                    (
                        func.coalesce(pay_subq.c.collection_sum, 0)
                        / year_pay_subq.c.collection_sum
                    )
                    * 100
                ).label("pct_collection_year"),
            )
            .join(
                PlanCat3,
                and_(
                    func.extract("year", PlanCat3.period) == credits_subq.c.year,
                    func.extract("month", PlanCat3.period) == credits_subq.c.month,
                    PlanCat3.category_id == 3,
                ),
                isouter=True,
            )
            .join(
                PlanCat4,
                and_(
                    func.extract("year", PlanCat4.period) == credits_subq.c.year,
                    func.extract("month", PlanCat4.period) == credits_subq.c.month,
                    PlanCat4.category_id == 4,
                ),
                isouter=True,
            )
            .join(
                pay_subq,
                and_(
                    pay_subq.c.year == credits_subq.c.year,
                    pay_subq.c.month == credits_subq.c.month,
                ),
                isouter=True,
            )
            .join(
                year_credits_subq,
                year_credits_subq.c.year == credits_subq.c.year,
                isouter=True,
            )
            .join(
                year_pay_subq,
                year_pay_subq.c.year == credits_subq.c.year,
                isouter=True,
            )
            .limit(limit)
            .offset(offset)
        )

        return await self.session.execute(q)
