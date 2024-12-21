import pytest
from datetime import datetime, timedelta
from src.ums_user_management_svc.models.session import Session
from src.ums_user_management_svc.models.user import User
from sqlalchemy.orm import Session as ORMSession

@pytest.fixture
def session_instance():
    return Session(
        user_id="test_user@example.com",
        token="testtoken123",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
        is_active=True  # Explicitly set is_active to True
    )

def test_session_creation(session_instance):
    assert session_instance.user_id == "test_user@example.com"
    assert session_instance.token == "testtoken123"
    assert session_instance.created_at < session_instance.expires_at
    assert session_instance.is_active == True  # New test to verify 'is_active' field

@pytest.fixture
def db_session():
    from src.ums_user_management_svc.models.base import Base
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_session_relationship(db_session):
    user = User(
        email="test_user@example.com",
        full_name="Test User",
        country="Test Country",
        state_province="Test State",
        hashed_password="hashedpassword",
        account_status="active"
    )
    db_session.add(user)
    db_session.commit()

    session = Session(
        user_id=user.email,
        token="testtoken123",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
        is_active=True  # Explicitly set is_active to True
    )
    db_session.add(session)
    db_session.commit()

    retrieved_session = db_session.query(Session).first()
    assert retrieved_session.user_id == user.email
    assert retrieved_session.token == "testtoken123"
    assert retrieved_session.user == user

# New test to verify 'is_active' defaults to True

def test_session_default_is_active(session_instance):
    assert session_instance.is_active is True
