from decimal import Decimal
from typing import Sequence, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.exc


from db import Dictionary
from db.credits_model import Credit
from db.payments_model import Payment
from db.users_model import User
from logs.config.logging_config import logger


class UserCreditRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_credits(self, user_id: int) -> Sequence[Credit]:

        if user_id <= 0:
            raise ValueError("User id must be a positive value")
        try:
            res = await self.session.execute(
                select(Credit).where(Credit.user_id == user_id)
            )
            return res.scalars().all()
        except sqlalchemy.exc.SQLAlchemyError as e:
            logger.error(f"Database error getting credits for user {user_id}: {e}")
            raise

    async def get_credit_total_payments(self, credit_id: int) -> Decimal:

        if credit_id <= 0:
            raise ValueError("Credit id must be a positive value")
        try:
            res = await self.session.execute(
                select(func.sum(Payment.sum)).where(Payment.credit_id == credit_id)
            )
            result = res.scalar()

            if result is None:
                return Decimal("0.0")
            if not isinstance(result, Decimal):
                return Decimal(str(result))
            return result
        except sqlalchemy.exc.SQLAlchemyError as e:
            logger.error(
                f"Database error fetching total payments for credit {credit_id}: {e}"
            )
            raise

    async def get_credit_payments_by_type(
        self, credit_id: int, type_id: int
    ) -> Decimal:

        if credit_id <= 0:
            raise ValueError("Credit id must be a positive value")
        if type_id <= 0:
            raise ValueError("Type id must be a positive value")
        try:
            res = await self.session.execute(
                select(func.sum(Payment.sum)).where(
                    Payment.credit_id == credit_id, Payment.type_id == type_id
                )
            )
            result = res.scalar()
            if result is None:
                return Decimal("0.0")
            if not isinstance(result, Decimal):
                return Decimal(str(result))
            return result
        except sqlalchemy.exc.SQLAlchemyError as e:
            logger.error(
                f"Database error fetching payments by type for credit {credit_id}, type {type_id}: {e}"
            )
            raise

    async def is_user_exists(self, user_id: int) -> bool:

        if user_id <= 0:
            raise ValueError("User id must be a positive value")
        try:
            res = await self.session.execute(select(User.id).where(User.id == user_id))
            return res.scalar_one_or_none() is not None
        except sqlalchemy.exc.SQLAlchemyError as e:
            logger.error(f"Database error checking if user {user_id} exists: {e}")
            raise

    async def get_payment_type_id(self, name: str) -> Optional[int]:
        if not name or not name.strip():
            raise ValueError("Payment type name must be non-empty")
        try:
            res = await self.session.execute(
                select(Dictionary.id).where(Dictionary.name == name)
            )
            return res.scalar_one_or_none()
        except sqlalchemy.exc.SQLAlchemyError as e:
            logger.error(f"Database error getting payment type id for '{name}': {e}")
            raise
