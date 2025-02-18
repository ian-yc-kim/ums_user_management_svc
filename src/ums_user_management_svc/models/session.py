from sqlalchemy import Column, String, ForeignKey, DateTime, Index, Integer, Boolean
from sqlalchemy.orm import relationship
from .base import Base
import sqlalchemy as sa

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.email'), nullable=False)
    token = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default=sa.true())
    
    user = relationship("User")

    __table_args__ = (
        Index('idx_sessions_user_id', 'user_id'),
        Index('idx_sessions_token', 'token'),
    )
