import jwt
import datetime
from typing import Any, Dict
from src.ums_user_management_svc.config import SECRET_KEY
import logging
from fastapi import HTTPException, status


def generate_token(payload: Dict[str, Any], expires_delta: datetime.timedelta = datetime.timedelta(hours=1)) -> str:
    try:
        payload.update({'exp': datetime.datetime.utcnow() + expires_delta})
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token
    except Exception as e:
        logging.error(e, exc_info=True)
        raise


def validate_token(token: str) -> Any:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError as e:
        logging.error("Token has expired.", exc_info=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired.")
    except jwt.InvalidTokenError as e:
        logging.error("Invalid token.", exc_info=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
