from sqlalchemy import Date, DECIMAL, ForeignKey, BigInteger

from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.connection import Base


class Credit(Base):
    __tablename__ = "credits"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    issuance_date: Mapped[Date] = mapped_column(Date, nullable=False)
    return_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    actual_return_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    body: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=True)
    percent: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="credits")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="credit")
