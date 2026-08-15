QUERY_POSTS = "{ posts { id title authorName createdAt } }"


def test_graphql_query_posts(client):
    res = client.post("/graphql", json={"query": QUERY_POSTS})
    assert res.status_code == 200
    body = res.json()
    assert "errors" not in body
    assert isinstance(body["data"]["posts"], list)


def test_graphql_create_requires_auth(client):
    res = client.post(
        "/graphql",
        json={"query": 'mutation { createPost(postData: { title: "x", content: "y" }) { id } }'},
    )
    assert res.status_code == 200
    errors = res.json()["errors"]
    assert errors[0]["message"] == "Not authenticated"


def test_graphql_create_update_delete(client, auth_headers):
    created = client.post(
        "/graphql",
        json={
            "query": 'mutation { createPost(postData: { title: "GQL Post", content: "body" }) { id title authorName } }'
        },
        headers=auth_headers,
    )
    assert created.status_code == 200
    data = created.json()["data"]["createPost"]
    assert data["authorName"] == "John Doe (Demo User)"
    post_id = data["id"]

    updated = client.post(
        "/graphql",
        json={
            "query": f'mutation {{ updatePost(id: {post_id}, postData: {{ title: "GQL Updated" }}) {{ id title }} }}'
        },
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["updatePost"]["title"] == "GQL Updated"

    deleted = client.post(
        "/graphql",
        json={"query": f"mutation {{ deletePost(id: {post_id}) }}"},
        headers=auth_headers,
    )
    assert deleted.status_code == 200
    assert deleted.json()["data"]["deletePost"] is True


def test_graphql_cannot_edit_others_post(client, auth_headers):
    post_id = client.post(
        "/graphql",
        json={
            "query": 'mutation { createPost(postData: { title: "Mine", content: "c" }) { id } }'
        },
        headers=auth_headers,
    ).json()["data"]["createPost"]["id"]

    client.post(
        "/api/auth/register",
        json={
            "username": "other2",
            "password": "pass1234",
            "email": "other2@example.com",
            "full_name": "Other Two",
        },
    )
    login = client.post(
        "/api/auth/login", json={"username": "other2", "password": "pass1234"}
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    edit = client.post(
        "/graphql",
        json={
            "query": f'mutation {{ updatePost(id: {post_id}, postData: {{ title: "Hack" }}) {{ id title }} }}'
        },
        headers=other_headers,
    )
    assert edit.status_code == 200
    assert edit.json()["errors"][0]["message"] == "You can only edit your own posts"
