from sqlalchemy import Column, String, Integer
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    state_province = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    account_status = Column(String, nullable=False, default='pending')
