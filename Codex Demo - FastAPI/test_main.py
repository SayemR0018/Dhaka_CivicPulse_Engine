from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from main import ALGORITHM, SECRET_KEY, app

client = TestClient(app)

def get_auth_headers():
    response = client.post(
        "/token",
        data={"username": "demo", "password": "secret"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def make_token(payload):
    token_payload = payload.copy()
    token_payload.setdefault("exp", datetime.now(timezone.utc) + timedelta(minutes=30))
    return jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

def make_auth_headers(payload):
    return {"Authorization": f"Bearer {make_token(payload)}"}

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Codex demo"}

def test_home_does_not_require_token():
    response = client.get("/", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Codex demo"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_health_does_not_require_token():
    response = client.get("/health", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_token_success():
    response = client.post(
        "/token",
        data={"username": "demo", "password": "secret"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]

    payload = jwt.decode(body["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "demo"
    assert "exp" in payload

def test_token_bad_password():
    response = client.post(
        "/token",
        data={"username": "demo", "password": "wrong"},
    )
    assert response.status_code == 401

def test_token_unknown_username():
    response = client.post(
        "/token",
        data={"username": "unknown", "password": "secret"},
    )
    assert response.status_code == 401

@pytest.mark.parametrize(
    "form_data",
    [
        {"password": "secret"},
        {"username": "demo"},
        {},
    ],
)
def test_token_requires_username_and_password(form_data):
    response = client.post("/token", data=form_data)
    assert response.status_code == 422

def test_add_requires_token():
    response = client.get("/add?a=2&b=3")
    assert response.status_code == 401

def test_multiply_requires_token():
    response = client.get("/multiply?a=2&b=3")
    assert response.status_code == 401

def test_power_requires_token():
    response = client.get("/power?a=2&b=3")
    assert response.status_code == 401

def test_factorial_requires_token():
    response = client.get("/factorial?n=5")
    assert response.status_code == 401

def test_multiply_rejects_invalid_token():
    response = client.get(
        "/multiply?a=2&b=3",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401

@pytest.mark.parametrize(
    "path",
    ["/add?a=2&b=3", "/multiply?a=2&b=3", "/power?a=2&b=3", "/factorial?n=5"],
)
def test_protected_endpoints_reject_expired_token(path):
    expired_token = make_token(
        {"sub": "demo", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}
    )
    response = client.get(path, headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401

@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"sub": "unknown"},
    ],
)
def test_protected_endpoints_reject_unusable_token(payload):
    response = client.get("/add?a=2&b=3", headers=make_auth_headers(payload))
    assert response.status_code == 401

def test_add():
    response = client.get("/add?a=2&b=3", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json() == {"result": 5}

def test_multiply():
    response = client.get("/multiply?a=2&b=3", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json() == {"result": 6}

def test_power():
    response = client.get("/power?a=2&b=3", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json() == {"result": 8}

def test_factorial():
    response = client.get("/factorial?n=5", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json() == {"result": 120}

@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/add?a=-2&b=3", {"result": 1}),
        ("/add?a=0&b=0", {"result": 0}),
        ("/add?a=1000000&b=2000000", {"result": 3000000}),
        ("/multiply?a=-2&b=3", {"result": -6}),
        ("/multiply?a=0&b=99", {"result": 0}),
        ("/multiply?a=1000&b=2000", {"result": 2000000}),
        ("/power?a=-2&b=3", {"result": -8}),
        ("/power?a=5&b=0", {"result": 1}),
        ("/power?a=10&b=3", {"result": 1000}),
        ("/factorial?n=0", {"result": 1}),
        ("/factorial?n=1", {"result": 1}),
        ("/factorial?n=6", {"result": 720}),
    ],
)
def test_math_edge_values(path, expected):
    response = client.get(path, headers=make_auth_headers({"sub": "demo"}))
    assert response.status_code == 200
    assert response.json() == expected

def test_factorial_rejects_negative_input():
    response = client.get("/factorial?n=-1", headers=get_auth_headers())
    assert response.status_code == 400
    assert response.json() == {"detail": "n must be non-negative"}

@pytest.mark.parametrize(
    "path",
    [
        "/add?b=3",
        "/add?a=2",
        "/add?a=two&b=3",
        "/add?a=2&b=three",
        "/multiply?b=3",
        "/multiply?a=2",
        "/multiply?a=two&b=3",
        "/multiply?a=2&b=three",
        "/power?b=3",
        "/power?a=2",
        "/power?a=two&b=3",
        "/power?a=2&b=three",
        "/factorial",
        "/factorial?n=five",
    ],
)
def test_math_query_validation(path):
    response = client.get(path, headers=make_auth_headers({"sub": "demo"}))
    assert response.status_code == 422
