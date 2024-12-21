import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from src.ums_user_management_svc.app import app
from src.ums_user_management_svc.models.user import User
from src.ums_user_management_svc.models.session import Session as UserSession
from src.ums_user_management_svc.utils.jwt import generate_token
from sqlalchemy.orm import Session as ORMSession
from src.ums_user_management_svc.config import SECRET_KEY
from src.ums_user_management_svc.config import get_db
import bcrypt
import jwt
from datetime import datetime, timedelta

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db_session():
    # Create a mock database session
    db = MagicMock(spec=ORMSession)
    return db

# Helper function to create a hashed password
def get_hashed_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def test_successful_login(client, mock_db_session):
    # Setup mock user
    user = User(
        email="test_user@example.com",
        hashed_password=get_hashed_password("password123"),
        account_status="active",
        failed_login_attempts=0
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = user
    
    # Mock the get_db dependency to return the mock_db_session
    app.dependency_overrides[get_db] = lambda: mock_db_session
    
    # Act
    response = client.post(
        "/login",
        json={"email": "test_user@example.com", "password": "password123"}
    )
    
    # Assert
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Cleanup
    app.dependency_overrides.clear()


def test_invalid_credentials(client, mock_db_session):
    # Setup mock user with a different password
    user = User(
        email="test_user@example.com",
        hashed_password=get_hashed_password("correct_password"),
        account_status="active",
        failed_login_attempts=0
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = user
    
    # Mock the get_db dependency
    app.dependency_overrides[get_db] = lambda: mock_db_session
    
    # Act
    response = client.post(
        "/login",
        json={"email": "test_user@example.com", "password": "wrong_password"}
    )
    
    # Assert
    assert response.status_code == 401
    
    # Cleanup
    app.dependency_overrides.clear()


def test_missing_fields(client, mock_db_session):
    # Mock the get_db dependency
    app.dependency_overrides[get_db] = lambda: mock_db_session
    
    # Missing password
    response = client.post(
        "/login",
        json={"email": "test_user@example.com"}
    )
    assert response.status_code == 422
    
    # Missing email
    response = client.post(
        "/login",
        json={"password": "password123"}
    )
    assert response.status_code == 422
    
    # Cleanup
    app.dependency_overrides.clear()


def test_invalid_email_format(client, mock_db_session):
    # Mock the get_db dependency
    app.dependency_overrides[get_db] = lambda: mock_db_session
    
    response = client.post(
        "/login",
        json={"email": "invalid_email", "password": "password123"}
    )
    assert response.status_code == 422
    
    # Cleanup
    app.dependency_overrides.clear()


def test_weak_password(client, mock_db_session):
    # Assuming password-validator is used for strength
    app.dependency_overrides[get_db] = lambda: mock_db_session
    
    response = client.post(
        "/login",
        json={"email": "test_user@example.com", "password": "123"}
    )
    assert response.status_code == 422
    
    # Cleanup
    app.dependency_overrides.clear()


def test_account_lockout_after_max_failed_attempts(client, mock_db_session):
    # Setup user with failed_login_attempts = MAX_FAILED_ATTEMPTS-1
    user = User(
        email="test_lockout@example.com",
        hashed_password=get_hashed_password("password123"),
        account_status="active",
        failed_login_attempts=4,  # Assuming MAX_FAILED_ATTEMPTS=5
        account_locked_until=None
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = user

    app.dependency_overrides[get_db] = lambda: mock_db_session

    # Attempt one more failed login
    response = client.post(
        "/login",
        json={"email": "test_lockout@example.com", "password": "wrong_password"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is locked due to too many failed login attempts."
    assert user.failed_login_attempts == 5
    assert user.account_locked_until is not None

    app.dependency_overrides.clear()


def test_locked_account_cannot_login(client, mock_db_session):
    # Setup user with account_locked_until in the future
    future_time = datetime.utcnow() + timedelta(minutes=15)
    user = User(
        email="locked_user@example.com",
        hashed_password=get_hashed_password("password123"),
        account_status="active",
        failed_login_attempts=5,
        account_locked_until=future_time
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = user

    app.dependency_overrides[get_db] = lambda: mock_db_session

    # Attempt to login
    response = client.post(
        "/login",
        json={"email": "locked_user@example.com", "password": "password123"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is locked. Please try again later."

    app.dependency_overrides.clear()


def test_successful_login_resets_failed_attempts(client, mock_db_session):
    # Setup user with failed_login_attempts >=1
    user = User(
        email="reset_attempts@example.com",
        hashed_password=get_hashed_password("password123"),
        account_status="active",
        failed_login_attempts=3,
        account_locked_until=None
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = user

    app.dependency_overrides[get_db] = lambda: mock_db_session

    # Successful login
    response = client.post(
        "/login",
        json={"email": "reset_attempts@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert user.failed_login_attempts == 0
    assert user.account_locked_until is None

    app.dependency_overrides.clear()
