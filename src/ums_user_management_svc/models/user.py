from sqlalchemy import Column, String
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    email = Column(String, primary_key=True, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    state_province = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    account_status = Column(String, nullable=False, server_default='pending')
