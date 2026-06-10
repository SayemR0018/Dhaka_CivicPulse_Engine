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
    assert response.json() == {"message": "Welcome to Dhaka CivicPulse API Hub"}

def test_home_does_not_require_token():
    response = client.get("/", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Dhaka CivicPulse API Hub"}

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

def test_triage_requires_token():
    response = client.post("/civic/triage", json={"report": "Fire at Sector 3"})
    assert response.status_code == 401

def test_triage_emergency_route(monkeypatch):
    from unittest.mock import MagicMock
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "dispatch_emergency_teams"
    mock_tool_call.function.arguments = '{"hazard_index": 8, "vulnerability_weight": 5}'
    
    mock_message.tool_calls = [mock_tool_call]
    mock_message.content = None
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    from main import openai_client
    monkeypatch.setattr(openai_client.chat.completions, "create", lambda **kwargs: mock_response)
    
    response = client.post(
        "/civic/triage",
        json={"report": "Emergency fire accident"},
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Critical Emergency Dispatched"
    assert response.json()["priority_key"] == 13

def test_triage_utility_route(monkeypatch):
    from unittest.mock import MagicMock
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "log_municipal_utility_ticket"
    mock_tool_call.function.arguments = '{"block_identifier": 5}'
    
    mock_message.tool_calls = [mock_tool_call]
    mock_message.content = None
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    from main import openai_client
    monkeypatch.setattr(openai_client.chat.completions, "create", lambda **kwargs: mock_response)
    
    response = client.post(
        "/civic/triage",
        json={"report": "Waterlogging in ward 5"},
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Municipal Ticket Logged"
    assert response.json()["routing_permutations"] == 120

def test_triage_unresolved_route(monkeypatch):
    from unittest.mock import MagicMock
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    
    mock_message.tool_calls = None
    mock_message.content = "Not enough details to categorize."
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    from main import openai_client
    monkeypatch.setattr(openai_client.chat.completions, "create", lambda **kwargs: mock_response)
    
    response = client.post(
        "/civic/triage",
        json={"report": "Hello there"},
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Unresolved Queue - Human Action Required"
    assert response.json()["detail"] == "Not enough details to categorize."
