# Dhaka CivicPulse Engine (FastAPI)

An AI-native urban calculation and telemetry framework optimized for assessing civic infrastructure failures, waterlogging risks, and emergency triage priority metrics across Dhaka City Corporation zones. The home and health routes are public, while all municipal calculation routes are secured via JWT bearer authentication layers.

![Alt Text](https://github.com/SayemR0018/Dhaka_CivicPulse_Engine/blob/108736f36759de71dbd7b9deee574280127aa7da/Dhaka%20CivicPulse%20Engine.png)

## Key Architectural Features
- **Deterministic Token Triage:** Uses strict data input models (a, b, n) to compute resource routing without risking generative AI hallucinations.
- **Automated Human Handoff Boundaries:** Hardcoded structural constraint flags trip 400 Bad Request exceptions or compile definitive sorting keys to seamlessly transition operational control to live human dispatchers.
- **Robust Security Perimeter:** Integrates OAuth2 password tracking and encrypted HS256 JWT validation protocols.

## Installation & Setup

1. Create and activate a isolated Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

2. Install the production-ready package dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Optional: Configure your environment signing keys:

```bash
export JWT_SECRET_KEY="replace-with-a-long-random-secret"
```

## Running the Engine

Start the local Uvicorn server:

```bash
uvicorn main:app --reload
```

Open your browser to inspect the interactive Swagger OpenAPI schemas: `http://127.0.0.1:8000/docs`

Execute the validation testing engine:

```bash
python -m pytest
```

## Municipal Endpoints Map

| Method | Path | Auth | System Description & Logic |
| --- | --- | --- | --- |
| `GET` | `/` | Open | Greets the client and registers API Hub connectivity. |
| `GET` | `/health` | Open | Returns active core status validation metrics. |
| `POST` | `/token` | Open | Verifies user credentials and issues secure bearer tokens. |
| `POST` | `/civic/triage` | Secured | [AI Orchestrator] Analyzes mixed-language (Bangla, English, Banglish) urban reports via LLM tool calling to route downstream to corresponding telemetry routes. |
| `GET` | `/add?a=<int>&b=<int>` | Secured | [Human Handoff] Evaluates hazard factors (a) and vulnerability indexes (b) to output a dispatcher sorting key. |
| `GET` | `/multiply?a=<int>&b=<int>` | Secured | Multiplies density parameters (a) by block scales (b) to track citizen impact footprint. |
| `GET` | `/power?a=<int>&b=<int>` | Secured | Calculates exponential risk acceleration where baseline severity (a) grows over time delay intervals (b). |
| `GET` | `/factorial?n=<int>` | Secured | Computes path permutations (n!) for utility vehicles; trips safety bounds if inputs run out of scale. |

*Demo Credentials — Username: `demo` | Password: `secret`*

## Operational Verification Examples

1. Request an access security key:

```bash
curl -X POST http://127.0.0.1:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=secret"
```

Response:

```json
{"access_token":"<your-jwt-token-string>","token_type":"bearer"}
```

2. Evaluate a priority dispatch sorting key via an authorized endpoint (e.g., `/add` with hazard index 12 and vulnerability weight 8):

```bash
TOKEN="<your-jwt-token-string>"
curl "http://127.0.0.1:8000/add?a=12&b=8" -H "Authorization: Bearer $TOKEN"
```

Response:

```json
{"result":20}
```

3. Submit an unstructured mixed-language civic complaint for AI multi-agent triage:

```bash
curl -X POST http://127.0.0.1:8000/civic/triage \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"report": "Mirpur block 5 a panic situation created due to severe waterlogging on main roads. Standard utilities are completely blocked."}'
```

Response:

```json
{
  "status": "Municipal Ticket Logged",
  "action_code": "FACTORIAL_ROUTE",
  "meta": {
    "block_identifier": 5
  },
  "routing_permutations": 120
}
```

## Interactive Streamlit Frontend Dashboard

The Dhaka CivicPulse Engine now runs an interactive frontend web application alongside the core API backend. This interface allows developers and administrators to ingest raw citizen reports and visualize live agent triage decisions in real time.

### Booting the UI Layer

Once the FastAPI backend server is running (`uvicorn main:app --reload`), you can start the Streamlit UI layer using:

```bash
python -m streamlit run app_ui.py
```
