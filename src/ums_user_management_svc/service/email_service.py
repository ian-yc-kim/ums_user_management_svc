import logging
from itsdangerous import URLSafeTimedSerializer
from fastapi import HTTPException
from src.ums_user_management_svc.config import SECRET_KEY, DOMAIN_URL
from src.ums_user_management_svc.models.user import User
from src.ums_user_management_svc.models.base import get_session
from sqlalchemy.orm import Session

serializer = URLSafeTimedSerializer(SECRET_KEY)

def send_verification_email(email: str) -> None:
    """Send a verification email to the specified email address."""
    try:
        token = serializer.dumps(email, salt='email-confirm-salt')
        verification_url = f"{DOMAIN_URL}/verify?token={token}"
        # Implement actual email sending logic here, e.g., using SMTP or an email service provider
        logging.info(f"Sending verification email to {email} with link: {verification_url}")
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail='Failed to send verification email')
