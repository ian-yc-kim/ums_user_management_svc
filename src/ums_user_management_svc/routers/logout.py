from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.ums_user_management_svc.utils.jwt import validate_token
from src.ums_user_management_svc.models.session import Session
from src.ums_user_management_svc.config import get_db
from sqlalchemy.future import select
from sqlalchemy.orm import Session as ORMSession
import logging

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/")
def logout(token: str = Depends(oauth2_scheme), db: ORMSession = Depends(get_db)):
    try:
        payload = validate_token(token)
        stmt = select(Session).where(Session.token == token, Session.is_active == True)
        result = db.execute(stmt)
        session = result.scalars().first()
        if not session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session or token.")
        session.is_active = False
        db.commit()
        return {"message": "Successfully logged out."}
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed.")
