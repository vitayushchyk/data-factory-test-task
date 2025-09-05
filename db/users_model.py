from sqlalchemy import BigInteger, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.connection import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    registration_date: Mapped[Date] = mapped_column(Date, nullable=False)

    credits: Mapped[list["Credit"]] = relationship("Credit", back_populates="user")
