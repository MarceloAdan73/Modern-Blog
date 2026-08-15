def test_dashboard_stats(client, auth_headers):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    body = res.json()
    assert body["total_users"] >= 1
    assert body["total_posts"] >= 0
    assert body["most_active_user"] == "user"


def test_user_stats(client):
    res = client.get("/api/users/1/stats")
    assert res.status_code == 200
    body = res.json()
    assert "total_posts" in body
    assert "total_words" in body
    assert "average_words_per_post" in body
    assert "last_post_date" in body
