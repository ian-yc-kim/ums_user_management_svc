import pytest
from fastapi.testclient import TestClient
from src.ums_user_management_svc.app import app
from src.ums_user_management_svc.models.user import User
from src.ums_user_management_svc.models.base import get_session
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_dependencies(db_session):
    def get_test_session():
        yield db_session
    app.dependency_overrides[get_session] = get_test_session
    yield
    app.dependency_overrides.clear()

@patch('src.ums_user_management_svc.routers.signup.send_verification_email')
def test_signup_success(mock_send_email, db_session):
    response = client.post('/signup', json={
        "email": "newuser@example.com",
        "full_name": "New User",
        "country": "Testland",
        "state_province": "Test State",
        "password": "Password1"
    })
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully. Please verify your email."}
    mock_send_email.assert_called_once_with("newuser@example.com")

@patch('src.ums_user_management_svc.routers.signup.send_verification_email')
def test_signup_duplicate_email(mock_send_email, db_session):
    # Create initial user
    user = User(
        email="duplicate@example.com",
        full_name="Existing User",
        country="Country",
        state_province="State",
        hashed_password="hashedpassword",
        account_status="pending"
    )
    db_session.add(user)
    db_session.commit()

    # Attempt to create duplicate user
    response = client.post('/signup', json={
        "email": "duplicate@example.com",
        "full_name": "New User",
        "country": "Testland",
        "state_province": "Test State",
        "password": "Password1"
    })
    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}
    mock_send_email.assert_not_called()

def test_signup_invalid_email():
    response = client.post('/signup', json={
        "email": "invalid-email",
        "full_name": "User",
        "country": "Country",
        "state_province": "State",
        "password": "Password1"
    })
    assert response.status_code == 422
    # Check that the detail contains error message about invalid email
    assert any(
        err['msg'] == 'value is not a valid email address: An email address must have an @-sign.'
        for err in response.json()['detail']
    )


def test_signup_weak_password():
    # Missing uppercase and number
    response = client.post('/signup', json={
        "email": "user2@example.com",
        "full_name": "User Two",
        "country": "Country",
        "state_province": "State",
        "password": "password"
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Password does not meet complexity requirements"}

def test_signup_missing_fields():
    response = client.post('/signup', json={
        "email": "",
        "full_name": "",
        "country": "",
        "state_province": "",
        "password": ""
    })
    assert response.status_code == 422  # Pydantic validation error
