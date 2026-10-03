import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Session as SessionModel
from app.models import User
from app.security import verify_password

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_at: datetime


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    stmt = select(User).where(User.username == credentials.username)
    user = db.execute(stmt).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Username or password is not correct")

    if verify_password(credentials.password, user.password_hash):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=14)

        new_session = SessionModel(user_id=user.id, token=token, expires_at=expires_at)
        db.add(new_session)
        db.commit()
        return LoginResponse(token=token, expires_at=expires_at)
    else:
        raise HTTPException(status_code=401, detail="Username or password is not correct")
