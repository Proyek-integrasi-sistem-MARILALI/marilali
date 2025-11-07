from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_and_login():
    # register user baru
    res = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "123456"
    })
    assert res.status_code == 201

    # login user
    res = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "123456"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()
