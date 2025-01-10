from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as ORMSession
from src.ums_user_management_svc.utils.jwt import validate_token
from src.ums_user_management_svc.config import get_db
from src.ums_user_management_svc.models.user import User
from src.ums_user_management_svc.models.session import Session
import logging

TERMINATED_STATUS = 'terminated'

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/")
def terminate_account(token: str = Depends(oauth2_scheme), db: ORMSession = Depends(get_db)):
    """
    Terminate the authenticated user's account.

    Args:
        token (str): JWT token for authentication.
        db (Session): Database session.

    Returns:
        dict: Success message upon successful termination.

    Raises:
        HTTPException: If token is invalid, user is not found, account is already terminated, or termination fails.
    """
    try:
        payload = validate_token(token)
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")
        
        # Retrieve the user
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
        if user.account_status == TERMINATED_STATUS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is already terminated.")
        
        # Update account_status to 'terminated'
        user.account_status = TERMINATED_STATUS

        # Invalidate all active sessions
        active_sessions = db.query(Session).filter(Session.user_id == user.email, Session.is_active == True).all()
        for session in active_sessions:
            session.is_active = False

        db.commit()

        return {"message": "Account successfully terminated."}
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Account termination failed.")
