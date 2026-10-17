import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_session, get_current_user
from app.models import Session as SessionModel
from app.models import User
from app.security import DUMMY_HASH, hash_token, verify_password

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
        verify_password(credentials.password, DUMMY_HASH)
        raise HTTPException(status_code=401, detail="Username or password is not correct")

    if verify_password(credentials.password, user.password_hash):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=14)

        new_session = SessionModel(
            user_id=user.id, token_hash=hash_token(token), expires_at=expires_at
        )
        db.add(new_session)
        db.commit()
        return LoginResponse(token=token, expires_at=expires_at)
    else:
        raise HTTPException(status_code=401, detail="Username or password is not correct")


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    created_at: datetime


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)):
    return user


# TODO add some fault handeling in case 2 logout requests are done at the same time
# (current version would cause error 500)
@router.post("/logout", status_code=204)
def logout(session_row: SessionModel = Depends(get_current_session), db: Session = Depends(get_db)):
    db.delete(session_row)
    db.commit()
