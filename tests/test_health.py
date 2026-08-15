def test_health_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["status"] == "healthy"
    assert body["database"] == "connected"
    assert body["version"] == "1.0"
    assert "timestamp" in body
