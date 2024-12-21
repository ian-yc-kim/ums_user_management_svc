from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from src.ums_user_management_svc.config import SECRET_KEY, DOMAIN_URL
from src.ums_user_management_svc.models.user import User
from src.ums_user_management_svc.models.base import get_session
import logging

serializer = URLSafeTimedSerializer(SECRET_KEY)

router = APIRouter()

@router.get('/')
def verify_email(token: str, db: Session = Depends(get_session)):
    try:
        email = serializer.loads(token, salt='email-confirm-salt', max_age=86400)
    except SignatureExpired as e:
        logging.error(f'SignatureExpired: {e} | Token length: {len(token)}', exc_info=True)
        raise HTTPException(status_code=400, detail='Verification link expired.')
    except BadSignature as e:
        logging.error(f'BadSignature: {e} | Token length: {len(token)}', exc_info=True)
        raise HTTPException(status_code=400, detail='Invalid verification token.')
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found.')
    if user.account_status == 'verified':
        return {'message': 'Account already verified.'}
    user.account_status = 'verified'
    db.commit()
    return {'message': 'Account successfully verified.'}
