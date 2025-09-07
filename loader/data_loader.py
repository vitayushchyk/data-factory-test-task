import pandas as pd
from typing import List, Any, Dict
import asyncio
from sqlalchemy import select
from db.users_model import User
from db.credits_model import Credit
from db.dictionary_model import Dictionary
from db.plans_model import Plan
from db.payments_model import Payment
from logs.config.logging_config import logger


class DataLoader:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    @staticmethod
    def _parse_dates(series: pd.Series, date_format: str = "%d.%m.%Y") -> pd.Series:
        return pd.to_datetime(
            series, format=date_format, errors="coerce"
        ).dt.date.where(series.notnull(), None)

    async def _read_csv_async(self, filename: str, sep: str = "\t") -> pd.DataFrame:

        return await asyncio.to_thread(pd.read_csv, filename, sep=sep)

    def _get_columns_map(self, model_cls: Any) -> Dict[str, str]:

        if model_cls.__name__ == "Dictionary":
            return {"id": "id", "name": "name"}
        if model_cls.__name__ == "User":
            return {
                "id": "id",
                "login": "login",
                "registration_date": "registration_date",
            }
        if model_cls.__name__ == "Plan":
            return {
                "id": "id",
                "period": "period",
                "sum": "sum",
                "category_id": "category_id",
            }
        if model_cls.__name__ == "Credit":
            return {
                "id": "id",
                "user_id": "user_id",
                "issuance_date": "issuance_date",
                "return_date": "return_date",
                "actual_return_date": "actual_return_date",
                "body": "body",
                "percent": "percent",
            }
        if model_cls.__name__ == "Payment":
            return {
                "id": "id",
                "sum": "sum",
                "payment_date": "payment_date",
                "credit_id": "credit_id",
                "type_id": "type_id",
            }
        raise ValueError(f"Unknown model: {model_cls.__name__}")

    async def _load_data(self, filename: str, model_cls: Any) -> List[Any]:
        df = await self._read_csv_async(filename)
        columns_map = self._get_columns_map(model_cls)

        for csv_col, model_attr in columns_map.items():
            if "date" in model_attr:
                df[csv_col] = self._parse_dates(df[csv_col])

        return [
            model_cls(
                **{
                    model_attr: row[csv_col]
                    for csv_col, model_attr in columns_map.items()
                }
            )
            for _, row in df.iterrows()
        ]

    async def import_all(self) -> None:

        tables_to_import = [
            {
                "model": Dictionary,
                "filename": "test_data/dictionary.csv",
                "name": "dictionaries",
            },
            {"model": User, "filename": "test_data/users.csv", "name": "users"},
            {"model": Plan, "filename": "test_data/plans.csv", "name": "plans"},
            {"model": Credit, "filename": "test_data/credits.csv", "name": "credits"},
            {
                "model": Payment,
                "filename": "test_data/payments.csv",
                "name": "payments",
            },
        ]

        async with self.session_maker() as session:
            for table_info in tables_to_import:
                model = table_info["model"]
                filename = table_info["filename"]
                name = table_info["name"]

                try:

                    result = await session.execute(select(model.id))
                    existing_ids = {row[0] for row in result.all()}

                    all_objs = await self._load_data(filename, model)
                    new_objs = [obj for obj in all_objs if obj.id not in existing_ids]

                    if new_objs:
                        session.add_all(new_objs)
                        logger.info(f"Imported {len(new_objs)} new {name}.")
                    else:
                        logger.warning(f"All {name} already exist in the database.")

                except Exception as e:
                    logger.error(f"Error importing {name}: {e}")

            await session.commit()
