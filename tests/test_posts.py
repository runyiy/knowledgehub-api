from tests.helpers import create_user, login_and_get_token, create_post_api, auth_headers

def test_get_post_public_anonymous_ok(client, db_session):
    create_user(db_session, username="alice", password="12345678")
    token = login_and_get_token(client, "alice", "12345678")

    post = create_post_api(
        client,
        token=token,
        title="public post",
        content="hello",
        is_public=True,
    )

    r = client.get(f"/api/posts/{post['id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == post["id"]
    assert data["is_public"] is True


def test_get_post_private_requires_auth_and_author(client, db_session):
    # alice creates a private post
    create_user(db_session, username="alice", password="12345678")
    alice_token = login_and_get_token(client, "alice", "12345678")

    private_post = create_post_api(
        client,
        token=alice_token,
        title="private post",
        content="secret",
        is_public=False,
    )

    # anonymous should be 401 (per your design)
    r = client.get(f"/api/posts/{private_post['id']}")
    assert r.status_code == 401, r.text

    # bob logged in but not author -> 403
    create_user(db_session, username="bob", password="12345678")
    bob_token = login_and_get_token(client, "bob", "12345678")

    r = client.get(
        f"/api/posts/{private_post['id']}",
        headers=auth_headers(bob_token),
    )
    assert r.status_code == 403, r.text

    # author -> 200
    r = client.get(
        f"/api/posts/{private_post['id']}",
        headers=auth_headers(alice_token),
    )
    assert r.status_code == 200
    assert r.json()["id"] == private_post["id"]


def test_patch_post_author_only(client, db_session):
    create_user(db_session, username="alice", password="12345678")
    alice_token = login_and_get_token(client, "alice", "12345678")
    post = create_post_api(
        client,
        token=alice_token,
        title="t1",
        content="c1",
        is_public=False,
    )

    create_user(db_session, username="bob", password="12345678")
    bob_token = login_and_get_token(client, "bob", "12345678")

    # non-author -> 403
    r = client.patch(
        f"/api/posts/{post['id']}",
        json={"title": "hacked"},
        headers=auth_headers(bob_token),
    )
    assert r.status_code == 403, r.text

    # author -> 200
    r = client.patch(
        f"/api/posts/{post['id']}",
        json={"title": "t2"},
        headers=auth_headers(alice_token),
    )
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "t2"


def test_delete_post_author_only(client, db_session):
    create_user(db_session, username="alice", password="12345678")
    alice_token = login_and_get_token(client, "alice", "12345678")
    post = create_post_api(
        client,
        token=alice_token,
        title="t1",
        content="c1",
        is_public=True,
    )

    create_user(db_session, username="bob", password="12345678")
    bob_token = login_and_get_token(client, "bob", "12345678")

    # non-author -> 403
    r = client.delete(
        f"/api/posts/{post['id']}",
        headers=auth_headers(bob_token),
    )
    assert r.status_code == 403, r.text

    # author -> 200/204 depending on your implementation
    r = client.delete(
        f"/api/posts/{post['id']}",
        headers=auth_headers(alice_token),
    )
    assert r.status_code in (200, 204), r.text


def test_list_posts_anonymous_only_public(client, db_session):
    create_user(db_session, username="alice", password="12345678")
    alice_token = login_and_get_token(client, "alice", "12345678")

    create_post_api(client, alice_token, "pub1", "c", True)
    create_post_api(client, alice_token, "priv1", "c", False)

    # anonymous list should only include public
    r = client.get("/api/posts")
    assert r.status_code == 200, r.text
    data = r.json()
    items = data["items"]

    assert isinstance(items, list)

    # all returned posts must be public
    assert all(p["is_public"] is True for p in items), items


def test_list_posts_mine_includes_private(client, db_session):
    create_user(db_session, username="alice", password="12345678")
    alice_token = login_and_get_token(client, "alice", "12345678")

    pub = create_post_api(client, alice_token, "pub", "c", True)
    priv = create_post_api(client, alice_token, "priv", "c", False)

    r = client.get(
        "/api/posts",
        params={"mine": "true"},
        headers=auth_headers(alice_token),
    )
    assert r.status_code == 200, r.text
    data = r.json()
    items = data["items"]
    ids = {p["id"] for p in items}

    assert pub["id"] in ids
    assert priv["id"] in ids


def test_posts_pagination_total_and_items(client, db_session):
    # Arrange: create user + token + 3 public posts
    create_user(db_session, username="alice", password="12345678")
    token = login_and_get_token(client, "alice", "12345678")

    p1 = create_post_api(client, token, "t1", "c1", True)
    p2 = create_post_api(client, token, "t2", "c2", True)
    p3 = create_post_api(client, token, "t3", "c3", True)

    # Act: page 1 (limit=2)
    r = client.get("/api/posts", params={"skip": 0, "limit": 2})
    assert r.status_code == 200, r.text

    data = r.json()
    assert data["skip"] == 0
    assert data["limit"] == 2
    assert data["total"] == 3
    assert len(data["items"]) == 2

    # Act: page 2 (skip=2, limit=2)
    r2 = client.get("/api/posts", params={"skip": 2, "limit": 2})
    assert r2.status_code == 200, r2.text

    data2 = r2.json()
    assert data2["skip"] == 2
    assert data2["limit"] == 2
    assert data2["total"] == 3
    assert len(data2["items"]) == 1

    returned_ids = {item["id"] for item in data["items"] + data2["items"]}
    assert returned_ids == {p1["id"], p2["id"], p3["id"]}


def test_posts_pagination_respects_visibility_for_anonymous(client, db_session):
    # Arrange: alice creates 2 public + 1 private
    create_user(db_session, username="alice", password="12345678")
    token = login_and_get_token(client, "alice", "12345678")

    pub1 = create_post_api(client, token, "pub1", "c", True)
    pub2 = create_post_api(client, token, "pub2", "c", True)
    _priv = create_post_api(client, token, "priv", "c", False)

    # Act: anonymous list
    r = client.get("/api/posts", params={"skip": 0, "limit": 10})
    assert r.status_code == 200, r.text
    data = r.json()

    # Assert: only public posts visible
    assert data["total"] == 2
    ids = {p["id"] for p in data["items"]}
    assert ids == {pub1["id"], pub2["id"]}
    assert all(p["is_public"] is True for p in data["items"])


def test_posts_pagination_mine_includes_private(client, db_session):
    # Arrange: alice has public + private; bob has a public too
    create_user(db_session, username="alice", password="12345678")
    alice_token = login_and_get_token(client, "alice", "12345678")

    a_pub = create_post_api(client, alice_token, "a_pub", "c", True)
    a_priv = create_post_api(client, alice_token, "a_priv", "c", False)

    create_user(db_session, username="bob", password="12345678")
    bob_token = login_and_get_token(client, "bob", "12345678")
    _b_pub = create_post_api(client, bob_token, "b_pub", "c", True)

    # Act: alice mine=true should return only alice posts (including private)
    r = client.get(
        "/api/posts",
        params={"mine": "true", "skip": 0, "limit": 10},
        headers=auth_headers(alice_token),
    )
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["total"] == 2
    ids = {p["id"] for p in data["items"]}
    assert ids == {a_pub["id"], a_priv["id"]}