from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate
from sqlalchemy import func


def create_post(
    db: Session,
    *,
    post_in: PostCreate,
    author_id: int,
) -> Post:
    post = Post(
        title=post_in.title,
        content=post_in.content,
        is_public=post_in.is_public,
        author_id=author_id,
    )
    try:
        db.add(post)
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(post)
    return post


def get_visible_posts(
    db: Session,
    *,
    current_user: User | None,
    skip: int = 0,
    limit: int = 20,
    mine: bool = False,
    is_public: bool | None = None,
) -> list[Post]:
    query = db.query(Post)

    if current_user is None:  # Not sign in only public
        query = query.filter(Post.is_public.is_(True))
    else:  # sign in
        if mine:  # only mine public and private
            query = query.filter(Post.author_id == current_user.id)
        else:  # all public and my private
            query = query.filter(
                (Post.is_public.is_(True)) | (Post.author_id == current_user.id)
            )

        if is_public is not None:  # filter by public
            query = query.filter(Post.is_public.is_(is_public))

    total = query.with_entities(func.count()).scalar() or 0

    query = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

    return query, total


def update_post(db: Session, *, post: Post, post_in: PostUpdate) -> Post:
    update_data = post_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(post, field, value)
    try:
        db.add(post)
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(post)
    return post


def get_post(db: Session, post_id: int) -> Post | None:
    return db.query(Post).filter(Post.id == post_id).first()


def delete_post(db: Session, *, post: Post) -> None:
    try:
        db.delete(post)
        db.commit()
    except Exception:
        db.rollback()
        raise
