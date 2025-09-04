from sqlalchemy import Column, Integer, Date, DECIMAL, ForeignKey

from sqlalchemy.orm import relationship, declarative_base

from db.connection import Base


class Credit(Base):
    __tablename__ = "credits"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    issuance_date = Column(Date, nullable=False)
    return_date = Column(Date)
    actual_return_date = Column(Date)
    body = Column(DECIMAL(10, 2))
    percent = Column(DECIMAL(12, 2))

    user = relationship("User", back_populates="credits")
    payments = relationship("Payment", back_populates="credit")
