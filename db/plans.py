from sqlalchemy import Column, Integer, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship

from db.connection import Base


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    period = Column(Date, nullable=False)
    sum = Column(DECIMAL(12, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("dictionary.id"))

    category = relationship("Dictionary", back_populates="plans")
