import pytest
from src.ums_user_management_svc.models.user import User
from src.ums_user_management_svc.models.session import Session
from src.ums_user_management_svc.utils.jwt import generate_token
from datetime import datetime, timedelta
import uuid

@pytest.fixture
def test_user(db_session):
    # Ensure the test user does not already exist
    existing_user = db_session.query(User).filter(User.email == 'test_user@example.com').first()
    if existing_user:
        db_session.delete(existing_user)
        db_session.commit()
    
    user = User(
        email='test_user@example.com',
        full_name='Test User',
        country='Testland',
        state_province='Test State',
        hashed_password='hashedpassword',
        account_status='active'
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def active_session(db_session, test_user):
    unique_id = str(uuid.uuid4())
    token = generate_token({'sub': test_user.email, 'jti': unique_id}, expires_delta=timedelta(hours=1))
    session = Session(
        user_id=test_user.email,
        token=token,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
        is_active=True
    )
    db_session.add(session)
    db_session.commit()
    return token

def test_successful_termination(test_user, active_session, client, db_session):
    headers = {'Authorization': f'Bearer {active_session}'}
    response = client.post('/terminate/', headers=headers)
    assert response.status_code == 200
    assert response.json() == {'message': 'Account successfully terminated.'}
    
    # Refresh the user instance to get updated data
    terminated_user = db_session.query(User).filter(User.email == test_user.email).first()
    assert terminated_user.account_status == 'terminated'
    
    # Verify all sessions are invalidated
    sessions = db_session.query(Session).filter_by(user_id=test_user.email).all()
    for session in sessions:
        assert not session.is_active

def test_invalid_token(client):
    headers = {'Authorization': 'Bearer invalidtoken'}
    response = client.post('/terminate/', headers=headers)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Invalid token.'}

def test_already_terminated_account(test_user, active_session, client, db_session):
    # First termination
    headers = {'Authorization': f'Bearer {active_session}'}
    response = client.post('/terminate/', headers=headers)
    assert response.status_code == 200
    
    # Attempt to terminate again
    response = client.post('/terminate/', headers=headers)
    assert response.status_code == 400
    assert response.json() == {'detail': 'Account is already terminated.'}

def test_expired_token(test_user, db_session, client):
    expired_token = generate_token({'sub': test_user.email, 'jti': str(uuid.uuid4())}, expires_delta=timedelta(seconds=-1))
    headers = {'Authorization': f'Bearer {expired_token}'}
    response = client.post('/terminate/', headers=headers)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Token has expired.'}
