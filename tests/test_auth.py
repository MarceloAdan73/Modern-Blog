def test_register_login_me(client):
    res = client.post(
        "/api/auth/register",
        json={
            "username": "alice",
            "password": "secret123",
            "email": "alice@example.com",
            "full_name": "Alice Doe",
        },
    )
    assert res.status_code == 200
    assert res.json()["username"] == "alice"

    login = client.post(
        "/api/auth/login", json={"username": "alice", "password": "secret123"}
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert login.json()["token_type"] == "bearer"

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "alice"
    assert me.json()["email"] == "alice@example.com"


def test_register_duplicate_username(client):
    res = client.post(
        "/api/auth/register",
        json={
            "username": "user",
            "password": "secret123",
            "email": "new@example.com",
            "full_name": "New User",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Username already registered"


def test_register_duplicate_email(client):
    res = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "password": "secret123",
            "email": "user@example.com",
            "full_name": "New User",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Email already registered"


def test_login_wrong_password(client):
    res = client.post(
        "/api/auth/login", json={"username": "user", "password": "wrongpass"}
    )
    assert res.status_code == 401


def test_me_without_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_update_profile(client, auth_headers):
    res = client.put(
        "/api/auth/profile",
        headers=auth_headers,
        json={"bio": "Backend developer", "location": "Argentina"},
    )
    assert res.status_code == 200
    assert res.json()["bio"] == "Backend developer"
    assert res.json()["location"] == "Argentina"


def test_delete_profile(client):
    client.post(
        "/api/auth/register",
        json={
            "username": "tempuser",
            "password": "secret123",
            "email": "temp@example.com",
            "full_name": "Temp User",
        },
    )
    login = client.post(
        "/api/auth/login", json={"username": "tempuser", "password": "secret123"}
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    deleted = client.delete("/api/auth/profile", headers=headers)
    assert deleted.status_code == 200

    after = client.post(
        "/api/auth/login", json={"username": "tempuser", "password": "secret123"}
    )
    assert after.status_code == 401
