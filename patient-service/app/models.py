from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    phone = Column(String(20))
    age = Column(Integer)
    gender = Column(String(20))
    address = Column(String(255))
    # Custom status fields
    status = Column(String(50), default="active")
    is_active = Column(Boolean, default=True)