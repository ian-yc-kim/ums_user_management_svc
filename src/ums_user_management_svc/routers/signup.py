from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, inspect
from password_validator import PasswordValidator
from email_validator import validate_email, EmailNotValidError
from bcrypt import gensalt, hashpw
from src.ums_user_management_svc.models.user import User
from src.ums_user_management_svc.models.base import get_session
from src.ums_user_management_svc.service.email_service import send_verification_email
from itsdangerous import URLSafeTimedSerializer
from src.ums_user_management_svc.config import SECRET_KEY, DOMAIN_URL
import logging

serializer = URLSafeTimedSerializer(SECRET_KEY)

class SignupRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)
    state_province: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)

class SignupResponse(BaseModel):
    message: str

router = APIRouter()

@router.post('/', response_model=SignupResponse)
def signup(user: SignupRequest, db: Session = Depends(get_session)):
    # Validate email format without checking deliverability
    try:
        validate_email(user.email, check_deliverability=False)
    except EmailNotValidError as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=400, detail='Invalid email format') from e

    # Debug: Print available tables in the current session
    try:
        inspector = inspect(db.get_bind())
        tables = inspector.get_table_names()
        logging.debug(f"Available tables in the current session: {tables}")
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail='Internal server error')

    # Check if email is already registered
    stmt = select(User).where(User.email == user.email)
    try:
        existing_user = db.execute(stmt).scalar_one_or_none()
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail='Database query failed')

    if existing_user:
        raise HTTPException(status_code=409, detail='Email already registered')

    # Validate password complexity
    schema = PasswordValidator()
    schema.min(8).has().uppercase().has().digits()
    if not schema.validate(user.password):
        raise HTTPException(status_code=400, detail='Password does not meet complexity requirements')

    # Hash the password
    try:
        hashed_password = hashpw(user.password.encode('utf-8'), gensalt()).decode('utf-8')
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail='Password hashing failed')

    # Create new user
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        country=user.country,
        state_province=user.state_province,
        hashed_password=hashed_password,
        account_status='pending'
    )
    db.add(new_user)
    try:
        db.commit()
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail='Database commit failed')

    # Send verification email
    try:
        send_verification_email(user.email)
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail='Failed to send verification email')

    return SignupResponse(message='User created successfully. Please verify your email.')
