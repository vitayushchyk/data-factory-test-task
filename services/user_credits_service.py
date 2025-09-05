from decimal import Decimal


from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from repo.user_credits_repo import UserCreditRepo
from schemas.credits_info_schema import CreditInfo, UserCreditsRes
from datetime import date


class UserCreditCRUD:
    def __init__(self, session: AsyncSession):
        self.repo = UserCreditRepo(session)

    async def get_all_user_credits(self, user_id: int):
        is_user_exists = await self.repo.is_user_exists(user_id)
        if not is_user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )
        body_payment_type_id = await self.repo.get_payment_type_id("тіло")
        percent_payment_type_id = await self.repo.get_payment_type_id("відсотки")
        if body_payment_type_id is None or percent_payment_type_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Payment types 'тіло' or 'відсотки' not found in dictionary.",
            )
        all_credits = await self.repo.get_user_credits(user_id)
        credits_list = [
            await self._credit_to_schema(
                credit, body_payment_type_id, percent_payment_type_id
            )
            for credit in all_credits
        ]
        return UserCreditsRes(user_id=user_id, credits=credits_list).model_dump(
            exclude_none=True
        )

    async def _credit_to_schema(
        self, credit, body_payment_type_id, percent_payment_type_id
    ):
        closed = credit.actual_return_date is not None

        if closed:
            # close credit
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
            # open credit
            return_date = credit.return_date
            today = date.today()
            days_overdue = (
                (today - return_date).days if return_date and today > return_date else 0
            )
            body_payments = await self.repo.get_credit_payments_by_type(
                credit.id, body_payment_type_id
            )
            percent_payments = await self.repo.get_credit_payments_by_type(
                credit.id, percent_payment_type_id
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
