import pytest
from sqlalchemy.exc import IntegrityError
from src.ums_user_management_svc.models import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

def test_create_user_valid(db_session):
    user = User(
        email='test@example.com',
        full_name='Test User',
        country='Test Country',
        state_province='Test State',
        hashed_password='hashedpassword123'
    )
    db_session.add(user)
    db_session.commit()
    assert user.id is not None

def test_create_user_duplicate_email(db_session):
    user1 = User(
        email='test@example.com',
        full_name='Test User',
        country='Test Country',
        state_province='Test State',
        hashed_password='hashedpassword123'
    )
    db_session.add(user1)
    db_session.commit()
    user2 = User(
        email='test@example.com',
        full_name='Test User 2',
        country='Another Country',
        state_province='Another State',
        hashed_password='anotherhashedpassword'
    )
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_user_non_nullable_fields(db_session):
    user = User(
        email=None,
        full_name='Test User',
        country='Test Country',
        state_province='Test State',
        hashed_password='hashedpassword123'
    )
    db_session.add(user)
    with pytest.raises(IntegrityError):
        db_session.commit()
