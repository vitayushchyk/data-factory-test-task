from sqlalchemy import Column, Integer, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from db.dictionary import Dictionary  # noqa

from db.connection import Base


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    sum = Column(DECIMAL(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    credit_id = Column(Integer, ForeignKey("credits.id"), nullable=False)
    type_id = Column(Integer, ForeignKey("dictionary.id"), nullable=False)

    credit = relationship("Credit", back_populates="payments")
    type = relationship(
        "Dictionary", back_populates="payments_type", foreign_keys="Payment.type_id"
    )
