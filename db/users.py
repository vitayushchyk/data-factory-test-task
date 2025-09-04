from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship

from db.connection import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    login = Column(String(100), unique=True, nullable=False)
    registration_date = Column(Date, nullable=False)

    credits = relationship("Credit", back_populates="user")
