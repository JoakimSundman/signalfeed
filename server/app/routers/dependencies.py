from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Session as SessionModel
from app.models import User
from app.security import hash_token

bearer_scheme = HTTPBearer(auto_error=False)

INVALID_TOKEN = "Invalid or missing token"


def get_current_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> SessionModel:
    if credentials is None:
        raise HTTPException(
            status_code=401, detail=INVALID_TOKEN, headers={"WWW-Authenticate": "Bearer"}
        )
    token_hash = hash_token(credentials.credentials)
    stmt = select(SessionModel).where(SessionModel.token_hash == token_hash)
    session_row = db.execute(stmt).scalar_one_or_none()
    if session_row is None:
        raise HTTPException(
            status_code=401, detail=INVALID_TOKEN, headers={"WWW-Authenticate": "Bearer"}
        )
    if session_row.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401, detail=INVALID_TOKEN, headers={"WWW-Authenticate": "Bearer"}
        )
    return session_row


def get_current_user(
    session_row: SessionModel = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, session_row.user_id)
    if user is None:
        raise HTTPException(
            status_code=401, detail=INVALID_TOKEN, headers={"WWW-Authenticate": "Bearer"}
        )
    return user
