from repo.plan_repo import PlanRepo


class YearPerformanceService:
    def __init__(self, session):
        self.repo = PlanRepo(session)

    async def get_year_performance(self, year: int, limit: int = 12, offset: int = 0):
        return await self.repo.get_stats(year, limit=limit, offset=offset)
