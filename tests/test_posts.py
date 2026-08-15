def test_create_post_requires_auth(client):
    res = client.post("/api/posts", json={"title": "x", "content": "y"})
    assert res.status_code == 401


def test_posts_crud_flow(client, auth_headers):
    created = client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Test Post", "content": "Some content", "excerpt": "brief"},
    )
    assert created.status_code == 200
    body = created.json()
    assert body["title"] == "Test Post"
    assert body["author_name"] == "John Doe (Demo User)"
    assert body["is_owner"] is True
    post_id = body["id"]

    listing = client.get("/api/posts")
    assert listing.status_code == 200
    assert any(p["id"] == post_id for p in listing.json())
    assert all(p["is_owner"] is False for p in listing.json())

    single = client.get(f"/api/posts/{post_id}")
    assert single.status_code == 200
    assert single.json()["title"] == "Test Post"

    updated = client.put(
        f"/api/posts/{post_id}",
        headers=auth_headers,
        json={"title": "Updated Post", "content": "New content"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated Post"

    my_posts = client.get("/api/posts/my-posts", headers=auth_headers)
    assert my_posts.status_code == 200
    assert any(p["id"] == post_id for p in my_posts.json())

    deleted = client.delete(f"/api/posts/{post_id}", headers=auth_headers)
    assert deleted.status_code == 200

    gone = client.get(f"/api/posts/{post_id}")
    assert gone.status_code == 404


def test_post_not_found(client):
    res = client.get("/api/posts/999")
    assert res.status_code == 404


def test_cannot_edit_or_delete_others_post(client, auth_headers):
    post_id = client.post(
        "/api/posts", headers=auth_headers, json={"title": "Mine", "content": "c"}
    ).json()["id"]

    client.post(
        "/api/auth/register",
        json={
            "username": "other",
            "password": "pass1234",
            "email": "other@example.com",
            "full_name": "Other User",
        },
    )
    login = client.post(
        "/api/auth/login", json={"username": "other", "password": "pass1234"}
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    edit = client.put(
        f"/api/posts/{post_id}",
        headers=other_headers,
        json={"title": "Hacked", "content": "x"},
    )
    assert edit.status_code == 403

    delete = client.delete(f"/api/posts/{post_id}", headers=other_headers)
    assert delete.status_code == 403
