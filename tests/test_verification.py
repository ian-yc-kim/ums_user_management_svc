import pytest
from fastapi.testclient import TestClient
from src.ums_user_management_svc.app import app
from src.ums_user_management_svc.models.user import User
from src.ums_user_management_svc.models.base import get_session
from unittest.mock import patch, MagicMock
from itsdangerous import SignatureExpired, BadSignature

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_dependencies(db_session):
    def get_test_session():
        yield db_session
    app.dependency_overrides[get_session] = get_test_session
    yield
    app.dependency_overrides.clear()

@patch('src.ums_user_management_svc.routers.verification.serializer.loads')
def test_verify_email_success(mock_loads, db_session):
    mock_loads.return_value = 'user@example.com'
    user = User(
        email='user@example.com',
        full_name='Test User',
        country='Testland',
        state_province='Test State',
        hashed_password='hashedpassword',
        account_status='pending'
    )
    db_session.add(user)
    db_session.commit()

    response = client.get('/verify', params={'token': 'valid_token'})

    assert response.status_code == 200
    assert response.json() == {'message': 'Account successfully verified.'}
    updated_user = db_session.query(User).filter(User.email == 'user@example.com').first()
    assert updated_user.account_status == 'verified'

@patch('src.ums_user_management_svc.routers.verification.serializer.loads')
def test_verify_email_expired_token(mock_loads, db_session):
    mock_loads.side_effect = SignatureExpired('Token expired')
    user = User(
        email='expired@example.com',
        full_name='Expired User',
        country='Testland',
        state_province='Test State',
        hashed_password='hashedpassword',
        account_status='pending'
    )
    db_session.add(user)
    db_session.commit()

    response = client.get('/verify', params={'token': 'expired_token'})

    assert response.status_code == 400
    assert response.json() == {'detail': 'Verification link expired.'}

@patch('src.ums_user_management_svc.routers.verification.serializer.loads')
def test_verify_email_invalid_token(mock_loads, db_session):
    mock_loads.side_effect = BadSignature('Invalid token')
    user = User(
        email='invalid@example.com',
        full_name='Invalid User',
        country='Testland',
        state_province='Test State',
        hashed_password='hashedpassword',
        account_status='pending'
    )
    db_session.add(user)
    db_session.commit()

    response = client.get('/verify', params={'token': 'invalid_token'})

    assert response.status_code == 400
    assert response.json() == {'detail': 'Invalid verification token.'}

def test_verify_email_already_verified(db_session):
    user = User(
        email='verified@example.com',
        full_name='Verified User',
        country='Testland',
        state_province='Test State',
        hashed_password='hashedpassword',
        account_status='verified'
    )
    db_session.add(user)
    db_session.commit()

    with patch('src.ums_user_management_svc.routers.verification.serializer.loads') as mock_loads:
        mock_loads.return_value = 'verified@example.com'
        response = client.get('/verify', params={'token': 'valid_token'})

    assert response.status_code == 200
    assert response.json() == {'message': 'Account already verified.'}
