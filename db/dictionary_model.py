from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.connection import Base


class Dictionary(Base):
    __tablename__ = "dictionary"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    plans: Mapped[list["Plan"]] = relationship("Plan", back_populates="category")
    payments_type: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="type", foreign_keys="Payment.type_id"
    )
