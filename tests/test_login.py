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
