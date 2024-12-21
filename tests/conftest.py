from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from src.ums_user_management_svc.models.base import Base

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()