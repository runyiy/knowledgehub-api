from tests.helpers import create_user, login_and_get_token


def test_me_requires_auth(client):
    r = client.get("/api/users/me")
    assert r.status_code == 401


def test_token_and_me_success(client, db_session):
    create_user(db_session, username="alice", password="12345678")
    token = login_and_get_token(client, "alice", "12345678")

    r = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "alice"


def test_token_wrong_password_401(client, db_session):
    create_user(db_session, username="bob", password="12345678")
    r = client.post(
        "/api/auth/token",
        data={"username": "bob", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 401