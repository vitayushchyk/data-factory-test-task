import calendar
from datetime import date

from repo.plan_repo import PlanRepo


class PlanPerformanceService:
    def __init__(self, session):
        self.repo = PlanRepo(session)

    async def get_performance(self, target_date: date):

        plans = await self.repo.get_plans_for_period(target_date)
        data = []
        for plan in plans:
            period_start = plan.period.replace(day=1)
            last_day = plan.period.replace(
                day=calendar.monthrange(plan.period.year, plan.period.month)[1]
            )
            period_to = min(last_day, target_date)

            actual_sum = await self.repo.get_actual_sum(
                plan.category, period_start, period_to
            )
            percent = float(actual_sum) / float(plan.sum) * 100 if plan.sum else 0.0

            data.append(
                dict(
                    period=str(plan.period),
                    category=plan.category,
                    plan_sum=plan.sum,
                    fact_sum=actual_sum,
                    percent=round(percent, 2),
                )
            )
        return data
