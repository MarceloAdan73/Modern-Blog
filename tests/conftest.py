import os
import tempfile

_tmp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from database import SessionLocal
from models.models import Post, User
from main import app, seed_demo_user


@pytest.fixture(autouse=True)
def reset_db():
    db = SessionLocal()
    try:
        db.query(Post).delete()
        db.query(User).delete()
        db.commit()
    finally:
        db.close()
    seed_demo_user()
    yield
    db = SessionLocal()
    try:
        db.query(Post).delete()
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    res = client.post(
        "/api/auth/login", json={"username": "user", "password": "123456"}
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
