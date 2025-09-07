from typing import BinaryIO, Callable, Any

from decimal import Decimal

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST

from db import Plan
from repo.plan_repo import PlanRepo

SUM = "сума"
PERIOD = "місяць плану"
CATEGORY = "назва категорії плану"
CATEGORY_ID = [3, 4]
REQUIRED_COLUMNS = [SUM, PERIOD, CATEGORY]


class PlanService:
    def __init__(self, session: AsyncSession):
        self.repo = PlanRepo(session)

    async def load_file(self, file: BinaryIO):
        raw = pd.read_excel(file)
        self._validate_all(raw)

        periods_and_categories = self._extract_periods_categories(raw)

        duplicates = await self.repo.check_exists(periods_and_categories)
        if duplicates:
            dup_list = [{"period": d[0], "category_id": d[1]} for d in duplicates]
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail=f"Found already existing plans for: {dup_list}",
            )

        plans = self._build_plans(raw)
        await self.repo.add_plans(plans)
        return {"success": True, "inserted": len(plans)}

    def _validate_all(self, raw: pd.DataFrame):
        self._validate_columns(raw)
        self._validate_sum(raw)
        self._validate_periods(raw)
        self._validate_categories(raw)

    def _validate_columns(self, raw: pd.DataFrame):
        missing = [col for col in REQUIRED_COLUMNS if col not in raw.columns]
        if missing:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Required columns missing: {missing}",
            )

    def _validate_sum(self, raw: pd.DataFrame):
        if not pd.api.types.is_numeric_dtype(raw[SUM]):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Column '{SUM}' must be numeric",
            )
        bad_rows = raw[raw[SUM].isnull() | (raw[SUM] < 0)]
        real_bad_rows = (bad_rows.index + 2).tolist()
        if not bad_rows.empty:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Sum cannot be empty or negative. Bad rows: {real_bad_rows}",
            )

    def _validate_periods(self, raw: pd.DataFrame):
        if not pd.api.types.is_datetime64_any_dtype(raw[PERIOD]):
            try:
                raw[PERIOD] = pd.to_datetime(raw[PERIOD])
            except Exception:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Period column must be convertible to date",
                )
        if not (raw[PERIOD].dt.day == 1).all():
            bad_rows = (raw[raw[PERIOD].dt.day != 1].index + 2).tolist()
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"First day of month must be 1, bad rows: {bad_rows}",
            )

    def _validate_categories(self, raw: pd.DataFrame):
        invalid = set(raw[CATEGORY].astype(int)) - set(CATEGORY_ID)
        if invalid:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Invalid categories: {invalid}, must be in {CATEGORY_ID}",
            )

    def _extract_rows(
        self, raw: pd.DataFrame, mapper: Callable[[Any, Any, Any], Any]
    ) -> list:
        result = []
        for _, row in raw.iterrows():
            period = row[PERIOD]
            period = period.date() if hasattr(period, "date") else period
            category_id = int(row[CATEGORY])
            sum_val = row[SUM]
            if pd.notnull(period) and pd.notnull(category_id):
                result.append(mapper(period, category_id, sum_val))
        return result

    def _extract_periods_categories(self, raw: pd.DataFrame) -> list[tuple[str, int]]:
        result = self._extract_rows(
            raw, lambda period, category_id, sum_val: (str(period), category_id)
        )
        return result

    def _build_plans(self, raw: pd.DataFrame) -> list[Plan]:
        result = self._extract_rows(
            raw,
            lambda period, category_id, sum: Plan(
                period=period, category_id=category_id, sum=Decimal(sum)
            ),
        )
        return result
