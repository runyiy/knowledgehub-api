from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate


def get_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user_in: UserCreate):
    hashed_password = get_password_hash(user_in.password)
    user = User(
        username=user_in.username, hashed_password=hashed_password, is_active=True
    )

    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(user)
    return user
