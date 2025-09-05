from sqlalchemy import BigInteger, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.connection import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sum: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=False)
    payment_date: Mapped[Date] = mapped_column(Date, nullable=False)
    credit_id: Mapped[int] = mapped_column(ForeignKey("credits.id"), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("dictionary.id"), nullable=False)

    credit: Mapped["Credit"] = relationship("Credit", back_populates="payments")
    type: Mapped["Dictionary"] = relationship(
        "Dictionary", back_populates="payments_type", foreign_keys=[type_id]
    )
