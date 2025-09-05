from sqlalchemy import BigInteger, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.connection import Base


class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    period: Mapped[Date] = mapped_column(Date, nullable=False)
    sum: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("dictionary.id"))

    category: Mapped["Dictionary"] = relationship("Dictionary", back_populates="plans")
