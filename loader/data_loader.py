import pandas as pd
from typing import List
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
    """
    Loads data from CSV files to database
    """

    @staticmethod
    def parse_dates(series: pd.Series, date_format: str = "%d.%m.%Y") -> pd.Series:
        return pd.to_datetime(
            series, format=date_format, errors="coerce"
        ).dt.date.where(series.notnull(), None)

    @staticmethod
    async def read_csv_async(filename: str, sep: str = "\t") -> pd.DataFrame:
        """Async read CSV file"""
        return await asyncio.to_thread(pd.read_csv, filename, sep=sep)

    async def load_dictionaries(self, filename: str) -> List[Dictionary]:
        """Load dictionaries from CSV file"""
        df = await self.read_csv_async(filename)
        return [
            Dictionary(id=int(row["id"]), name=row["name"]) for _, row in df.iterrows()
        ]

    async def load_users(self, filename: str) -> List[User]:
        """Load users from CSV file"""
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
        """Load plans from CSV file"""
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
        """Load credits from CSV file"""
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
        """Load payments from CSV file"""
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

    async def import_all(self) -> None:
        """
        Import all data, skipping existing rows by id
        """
        async with async_session_maker() as session:
            # Dictionaries
            result = await session.execute(select(Dictionary.id))
            existing_dict_ids = {row[0] for row in result.all()}
            dict_objs = await self.load_dictionaries("test_data/dictionary.csv")
            new_dicts = [obj for obj in dict_objs if obj.id not in existing_dict_ids]
            if new_dicts:
                session.add_all(new_dicts)
                logger.info(f"Imported {len(new_dicts)} dictionaries.")
            else:
                logger.warning("Dictionaries already up-to-date.")

            # Users
            result = await session.execute(select(User.id))
            existing_user_ids = {row[0] for row in result.all()}
            user_objs = await self.load_users("test_data/users.csv")
            new_users = [obj for obj in user_objs if obj.id not in existing_user_ids]
            if new_users:
                session.add_all(new_users)
                logger.info(f"Imported {len(new_users)} users.")
            else:
                logger.warning("Users already up-to-date.")

            # Plans
            result = await session.execute(select(Plan.id))
            existing_plan_ids = {row[0] for row in result.all()}
            plan_objs = await self.load_plans("test_data/plans.csv")
            new_plans = [obj for obj in plan_objs if obj.id not in existing_plan_ids]
            if new_plans:
                session.add_all(new_plans)
                logger.info(f"Imported {len(new_plans)} plans.")
            else:
                logger.warning("Plans already up-to-date.")

            # Credits
            result = await session.execute(select(Credit.id))
            existing_credit_ids = {row[0] for row in result.all()}
            credit_objs = await self.load_credits("test_data/credits.csv")
            new_credits = [
                obj for obj in credit_objs if obj.id not in existing_credit_ids
            ]
            if new_credits:
                session.add_all(new_credits)
                logger.info(f"Imported {len(new_credits)} credits.")
            else:
                logger.warning("Credits already up-to-date.")

            # Payments
            result = await session.execute(select(Payment.id))
            existing_payment_ids = {row[0] for row in result.all()}
            payment_objs = await self.load_payments("test_data/payments.csv")
            new_payments = [
                obj for obj in payment_objs if obj.id not in existing_payment_ids
            ]
            if new_payments:
                session.add_all(new_payments)
                logger.info(f"Imported {len(new_payments)} payments.")
            else:
                logger.warning("Payments already up-to-date.")

            await session.commit()


if __name__ == "__main__":
    loader = DataLoader()
    asyncio.run(loader.import_all())
