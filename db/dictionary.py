from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

from db.connection import Base


class Dictionary(Base):
    __tablename__ = "dictionary"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    plans = relationship("Plan", back_populates="category")
    payments_type = relationship(
        "Payment", back_populates="type", foreign_keys="Payment.type_id"
    )
