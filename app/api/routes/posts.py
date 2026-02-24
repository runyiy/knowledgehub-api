from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_user_optional
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostRead, PostListResponse
from app.crud.post import (
    create_post,
    get_post,
    update_post,
    delete_post,
    get_visible_posts,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("", response_model=PostListResponse)
def read_posts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    current_user: User | None = Depends(get_current_user_optional),
    mine: bool = False,
    is_public: bool | None = None,
):
    if current_user is None:
        if mine:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        if is_public is False:
            return {"items": [], "total": 0, "skip": skip, "limit": limit}

    items, total = get_visible_posts(
        db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        mine=mine,
        is_public=is_public,
    )

    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{post_id}", response_model=PostRead)
def read_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if not post.is_public:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        if post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )
    return post


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_new_post(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    author_id = current_user.id
    return create_post(db, post_in=post_in, author_id=author_id)


@router.patch("/{post_id}", response_model=PostRead, status_code=status.HTTP_200_OK)
def update_existing_post(
    post_id: int,
    post_in: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = get_post(db, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return update_post(db, post=post, post_in=post_in)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = get_post(db, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    delete_post(db, post=post)
    return None
