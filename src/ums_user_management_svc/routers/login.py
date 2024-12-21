from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.ums_user_management_svc.schemas.login import LoginRequest, LoginResponse
from src.ums_user_management_svc.models.user import User
from src.ums_user_management_svc.models.session import Session as UserSession
from src.ums_user_management_svc.utils.jwt import generate_token
from src.ums_user_management_svc.config import get_db
import bcrypt
import logging
from datetime import datetime, timedelta

router = APIRouter()

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

def authenticate_user(db: Session, email: str, password: str) -> User:
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if user.account_locked_until and datetime.utcnow() < user.account_locked_until:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Account is locked. Please try again later.')
        if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.account_locked_until = datetime.utcnow() + LOCKOUT_DURATION
                db.commit()
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Account is locked due to too many failed login attempts.')
            db.commit()
            return None
        if user.account_status != 'active':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Account is not active.')
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.account_locked_until = None
        db.commit()
        return user
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error.')

@router.post('/', response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, request.email, request.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials.')

        # Generate JWT token
        access_token = generate_token({'sub': user.email}, expires_delta=timedelta(hours=1))

        # Create session entry
        session = UserSession(
            user_id=user.email,
            token=access_token,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(session)
        db.commit()

        return LoginResponse(access_token=access_token, token_type='bearer')
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error.')