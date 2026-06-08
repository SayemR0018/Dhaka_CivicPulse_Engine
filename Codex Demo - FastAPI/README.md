# Codex Demo FastAPI App

A small FastAPI API with JWT bearer authentication. The home route is public, and the math routes require a valid access token.

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Optional: set a custom JWT signing key. If this is not set, the app uses a local development fallback.

```bash
export JWT_SECRET_KEY="replace-with-a-long-random-secret"
```

## Running

Start the API server:

```bash
uvicorn main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Run tests:

```bash
python -m pytest
```

## Endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/` | No | Returns a welcome message. |
| `GET` | `/health` | No | Returns API health status. |
| `POST` | `/token` | No | Accepts OAuth2 form login and returns a JWT bearer token. |
| `GET` | `/add?a=<int>&b=<int>` | Yes | Returns the sum of `a + b`. |
| `GET` | `/multiply?a=<int>&b=<int>` | Yes | Returns the product of `a * b`. |
| `GET` | `/power?a=<int>&b=<int>` | Yes | Returns `a` raised to the power of `b`. |
| `GET` | `/factorial?n=<int>` | Yes | Returns `n!` for a non-negative integer. |

Demo credentials:

```text
username: demo
password: secret
```

## Examples

Call the public home endpoint:

```bash
curl http://127.0.0.1:8000/
```

Response:

```json
{"message":"Hello from Codex demo"}
```

Call the public health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{"status":"ok"}
```

Request an access token:

```bash
curl -X POST http://127.0.0.1:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=secret"
```

Response:

```json
{"access_token":"<jwt>","token_type":"bearer"}
```

Use the token with `/add`:

```bash
TOKEN="<jwt>"

curl "http://127.0.0.1:8000/add?a=2&b=3" \
  -H "Authorization: Bearer $TOKEN"
```

Response:

```json
{"result":5}
```

Use the token with `/multiply`:

```bash
curl "http://127.0.0.1:8000/multiply?a=2&b=3" \
  -H "Authorization: Bearer $TOKEN"
```

Response:

```json
{"result":6}
```

Use the token with `/power`:

```bash
curl "http://127.0.0.1:8000/power?a=2&b=3" \
  -H "Authorization: Bearer $TOKEN"
```

Response:

```json
{"result":8}
```

Use the token with `/factorial`:

```bash
curl "http://127.0.0.1:8000/factorial?n=5" \
  -H "Authorization: Bearer $TOKEN"
```

Response:

```json
{"result":120}
```

Calling a protected endpoint without a valid token returns `401 Unauthorized`.
