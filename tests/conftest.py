import src.ums_user_management_svc.models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from sqlalchemy.pool import StaticPool
from src.ums_user_management_svc.models.base import Base

@pytest.fixture(scope='function')
def db_session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()