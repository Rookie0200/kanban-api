from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.core.database import SessionLocal
from app import models
from app import security
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # print("controle inside get_current_user with token :",token)
    from jose import JWTError
    try:
        payload = security.decode_access_token(token)
        print("the payload has :", payload)
        user_id = uuid.UUID(payload.get("sub"))
        # print("the user_id inside get_current_user is :", user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    user = db.get(models.user.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
