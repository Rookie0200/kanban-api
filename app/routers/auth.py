from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.deps import get_db
from app.services import user_service
from app.security import create_access_token
from app.schemas.auth import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token")
def login_for_access_token(data:LoginRequest, db: Session = Depends(get_db)):
    print("inside the login route")
    user = user_service.authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
