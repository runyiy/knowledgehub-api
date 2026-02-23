from sqlite3 import IntegrityError

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserRead, UserCreate
from app.crud.user import get_by_username, create_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
        user_in : UserCreate,
        db: Session = Depends(get_db),
):
    existing = get_by_username(db, user_in.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    try:
        user = create_user(db, user_in)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    return user