from typing import Generator
from fastapi.security import (
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
    HTTPBearer,
)
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.db.session as db_session
from app.models.user import User
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
bearer_optional = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    if db_session.SessionLocal is None:
        # init_engine not running yet
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database is not initialized. Call init_engine() first.",
        )
    db = db_session.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_access_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.get(User, user_id_int)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return user


def get_current_user_optional(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_optional),
    db: Session = Depends(get_db),
) -> User | None:
    if not creds or creds.scheme.lower() != "bearer":
        return None
    user_id = decode_access_token(creds.credentials)
    if not user_id:
        return None
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.get(User, user_id_int)
    if not user:
        return None
    return user
