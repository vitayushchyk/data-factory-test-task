import pandas as pd
from typing import List, Type, Callable, Any
import asyncio
from sqlalchemy import select
from db.connection import async_session_maker
from db.users_model import User
from db.credits_model import Credit
from db.dictionary_model import Dictionary
from db.plans_model import Plan
from db.payments_model import Payment
from logs.config.logging_config import logger


class DataLoader:
    @staticmethod
    def parse_dates(series: pd.Series, date_format: str = "%d.%m.%Y") -> pd.Series:
        try:
            parsed = pd.to_datetime(series, format=date_format, errors="coerce")
            return parsed.dt.date.where(series.notnull(), None)
        except Exception as e:
            logger.error(f"Failed to parse dates: {e}")
            raise

    @staticmethod
    async def read_csv_async(filename: str, sep: str = "\t") -> pd.DataFrame:
        try:
            return await asyncio.to_thread(pd.read_csv, filename, sep=sep)
        except Exception as e:
            logger.error(f"Failed to load CSV file {filename}: {e}")
            raise

    async def load_dictionaries(self, filename: str) -> List[Dictionary]:
        df = await self.read_csv_async(filename)
        return [
            Dictionary(id=int(row["id"]), name=row["name"]) for _, row in df.iterrows()
        ]

    async def load_users(self, filename: str) -> List[User]:

        df = await self.read_csv_async(filename)
        df["registration_date"] = self.parse_dates(df["registration_date"])
        return [
            User(
                id=int(row["id"]),
                login=row["login"],
                registration_date=row["registration_date"],
            )
            for _, row in df.iterrows()
        ]

    async def load_plans(self, filename: str) -> List[Plan]:

        df = await self.read_csv_async(filename)
        df["period"] = self.parse_dates(df["period"])
        return [
            Plan(
                id=int(row["id"]),
                period=row["period"],
                sum=row["sum"],
                category_id=row["category_id"],
            )
            for _, row in df.iterrows()
        ]

    async def load_credits(self, filename: str) -> List[Credit]:

        df = await self.read_csv_async(filename)
        for col in ["issuance_date", "return_date", "actual_return_date"]:
            df[col] = self.parse_dates(df[col])
        return [
            Credit(
                id=int(row["id"]),
                user_id=row["user_id"],
                issuance_date=row["issuance_date"],
                return_date=row["return_date"],
                actual_return_date=row["actual_return_date"],
                body=row["body"],
                percent=row["percent"],
            )
            for _, row in df.iterrows()
        ]

    async def load_payments(self, filename: str) -> List[Payment]:

        df = await self.read_csv_async(filename)
        df["payment_date"] = self.parse_dates(df["payment_date"])
        return [
            Payment(
                id=int(row["id"]),
                sum=row["sum"],
                payment_date=row["payment_date"],
                credit_id=row["credit_id"],
                type_id=row["type_id"],
            )
            for _, row in df.iterrows()
        ]

    async def _import_data(
        self,
        session,
        model_cls: Type,
        csv_loader: Callable[[str], Any],
        filename: str,
        log_label: str,
        id_field: str = "id",
    ):

        result = await session.execute(select(getattr(model_cls, id_field)))
        existing_ids = {row[0] for row in result.all()}
        objs = await csv_loader(filename)
        new_objs = [obj for obj in objs if getattr(obj, id_field) not in existing_ids]

        if new_objs:
            session.add_all(new_objs)
            logger.info(f"Imported {len(new_objs)} {log_label}.")
        else:
            logger.warning(f"{log_label.capitalize()} already up-to-date.")

    async def import_all(self) -> None:

        async with async_session_maker() as session:
            await self._import_data(
                session,
                Dictionary,
                self.load_dictionaries,
                "test_data/dictionary.csv",
                "dictionaries",
            )
            await self._import_data(
                session, User, self.load_users, "test_data/users.csv", "users"
            )
            await self._import_data(
                session, Plan, self.load_plans, "test_data/plans.csv", "plans"
            )
            await self._import_data(
                session, Credit, self.load_credits, "test_data/credits.csv", "credits"
            )
            await self._import_data(
                session,
                Payment,
                self.load_payments,
                "test_data/payments.csv",
                "payments",
            )
            await session.commit()


if __name__ == "__main__":
    loader = DataLoader()
    asyncio.run(loader.import_all())
