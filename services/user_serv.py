from decimal import Decimal

from sqlalchemy import select
from fastapi import HTTPException
from db.users import User, UserCreditRepo
from schemas.user_credits_schema import CreditInfo, UserCreditsRes
from datetime import date


BODY_PAYMENT_TYPE_ID = 1
PERCENT_PAYMENT_TYPE_ID = 2


class UserCreditCRUD:
    def __init__(self, session):
        self.repo = UserCreditRepo(session)

    async def get_user_credits_full(self, user_id: int):
        """ "Get all user credits"""
        is_user_exists = await self.repo.is_user_exists(user_id)
        if not is_user_exists:
            raise HTTPException(status_code=404, detail="User not found.")
        get_all_cred = await self.repo.get_user_credits(user_id)
        credits_list = [await self._credit_to_schema(credit) for credit in get_all_cred]
        return UserCreditsRes(user_id=user_id, credits=credits_list)

    async def _credit_to_schema(self, credit):
        closed = credit.actual_return_date is not None

        if closed:
            total_payments = await self.repo.get_credit_total_payments(credit.id)
            return CreditInfo(
                credit_id=credit.id,
                issuance_date=credit.issuance_date,
                closed=True,
                actual_return_date=credit.actual_return_date,
                body=Decimal(credit.body or 0),
                percent=Decimal(credit.percent or 0),
                total_payments=Decimal(total_payments),
                return_date=None,
                days_overdue=None,
                body_payments=None,
                percent_payments=None,
            )
        else:
            return_date = credit.return_date
            today = date.today()
            days_overdue = (
                (today - return_date).days if return_date and today > return_date else 0
            )
            body_payments = await self.repo.get_credit_payments_by_type(
                credit.id, BODY_PAYMENT_TYPE_ID
            )
            percent_payments = await self.repo.get_credit_payments_by_type(
                credit.id, PERCENT_PAYMENT_TYPE_ID
            )
            return CreditInfo(
                credit_id=credit.id,
                issuance_date=credit.issuance_date,
                closed=False,
                actual_return_date=None,
                body=Decimal(credit.body or 0),
                percent=Decimal(credit.percent or 0),
                total_payments=None,
                return_date=return_date,
                days_overdue=days_overdue,
                body_payments=Decimal(body_payments),
                percent_payments=Decimal(percent_payments),
            )
