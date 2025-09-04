from sqlalchemy import Column, Integer, String, Date, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from db.connection import Base
from db.credits import Credit
from db.payments import Payment


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    login = Column(String(100), unique=True, nullable=False)
    registration_date = Column(Date, nullable=False)

    credits = relationship("Credit", back_populates="user")


class UserCreditRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_credits(self, user_id: int):
        res = await self.session.execute(
            select(Credit).where(Credit.user_id == user_id)
        )
        return res.scalars().all()

    async def get_credit_total_payments(self, credit_id: int):
        res = await self.session.execute(
            select(func.sum(Payment.sum)).where(Payment.credit_id == credit_id)
        )
        return res.scalar() or 0

    async def get_credit_payments_by_type(self, credit_id: int, type_id: int):
        res = await self.session.execute(
            select(func.sum(Payment.sum)).where(
                Payment.credit_id == credit_id, Payment.type_id == type_id
            )
        )
        return res.scalar() or 0

    async def is_user_exists(self, user_id: int):
        res = await self.session.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none() is not None
