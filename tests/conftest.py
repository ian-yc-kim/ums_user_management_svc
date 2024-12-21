import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.ums_user_management_svc.models.base import Base
from src.ums_user_management_svc.models import User, Session
from src.ums_user_management_svc.config import get_db
from fastapi.testclient import TestClient

# Create a new file-based SQLite database for testing
TEST_DATABASE_URL = "sqlite:///test.db"

environment = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=environment)

# Import models to ensure tables are created
Base.metadata.create_all(bind=environment)

@pytest.fixture(scope="session")
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="module")
def client(db_session):
    from src.ums_user_management_svc.app import app
    # Override the get_db dependency to use the testing session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides[get_db] = get_db
