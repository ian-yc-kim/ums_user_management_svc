import pytest
from fastapi.testclient import TestClient
from src.ums_user_management_svc.app import app
from src.ums_user_management_svc.utils.jwt import generate_token
from src.ums_user_management_svc.models.session import Session
from src.ums_user_management_svc.models.user import User
from sqlalchemy.orm import Session as ORMSession
from datetime import datetime, timedelta

# Removed the local 'client' fixture to use the one from conftest.py

def test_logout_success(client: TestClient, db_session: ORMSession):
    # Setup user and session
    user = User(email="test_user@example.com",
                full_name="Test User",
                country="Test Country",
                state_province="Test State",
                hashed_password="hashedpassword",
                account_status="active")
    db_session.add(user)
    db_session.commit()
    token = generate_token({"user_id": user.email})
    session = Session(user_id=user.email,
                      token=token,
                      created_at=datetime.utcnow(),
                      expires_at=datetime.utcnow() + timedelta(hours=1),
                      is_active=True)
    db_session.add(session)
    db_session.commit()

    # Perform logout
    response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out."}

    # Verify session is inactive
    updated_session = db_session.query(Session).filter(Session.token == token).first()
    assert updated_session.is_active == False

def test_logout_invalid_token(client: TestClient):
    response = client.post("/logout", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}

def test_logout_expired_token(client: TestClient, db_session: ORMSession):
    # Setup user and expired session
    user = User(email="expired_user@example.com",
                full_name="Expired User",
                country="Test Country",
                state_province="Test State",
                hashed_password="hashedpassword",
                account_status="active")
    db_session.add(user)
    db_session.commit()
    token = generate_token({"user_id": user.email}, expires_delta=timedelta(seconds=-1))
    session = Session(user_id=user.email,
                      token=token,
                      created_at=datetime.utcnow() - timedelta(hours=2),
                      expires_at=datetime.utcnow() - timedelta(hours=1),
                      is_active=True)
    db_session.add(session)
    db_session.commit()

    # Attempt logout with expired token
    response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Token has expired."}