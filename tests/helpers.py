# tests/helpers.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash
from typing import Any


def create_user(db: Session, username: str, password: str = "pass12345") -> User:
    user = User(
        username=username, hashed_password=get_password_hash(password), is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_and_get_token(client, username: str, password: str) -> str:
    resp = client.post(
        "/api/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_post_api(
    client,
    token: str,
    title: str,
    content: str,
    is_public: bool = True,
) -> dict[str, Any]:
    r = client.post(
        "/api/posts",
        json={"title": title, "content": content, "is_public": is_public},
        headers=auth_headers(token),
    )
    assert r.status_code in (200, 201), r.text
    return r.json()
