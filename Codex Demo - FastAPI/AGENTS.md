# AGENTS.md

## Core Workflow Rules
- Every municipal optimization endpoint must have full automated test suites.
- Use strict Python type hints to ensure data integrity during real-time triage.
- Return pure JSON payloads for rapid integration with human field agent dashboards.
- Execute and pass full `pytest` verification loops prior to deployment.

## Live Tool Architecture Maps
The Supervisor Agent (FastAPI `/civic/triage` endpoint) orchestrates two primary municipal dispatch tools using OpenAI function calling:

1. **`dispatch_emergency_teams`**:
   - **Trigger Criteria:** High-severity hazards, fires, building damage, or road accidents with injuries.
   - **Parameters:** `hazard_index` (1-10), `vulnerability_weight` (1-10).
   - **Downstream Route:** Add Route (`/add` endpoint) to calculate emergency priority key.

2. **`log_municipal_utility_ticket`**:
   - **Trigger Criteria:** Municipal infrastructure items like waterlogging, open sewers, or broken utility grids.
   - **Parameters:** `block_identifier` (ward/sector code block number).
   - **Downstream Route:** Factorial Route (`/factorial` endpoint) to compute routing path permutations.

## Cognitive Architectural Limits & Human Handoff
1. **The Core Task Execution:** The automated layers handle complex statistical computations (such as cascading utility risk evaluation and block permutation layouts).
2. **The Human Handoff Threshold:** The system establishes automated boundaries. If structural permutations overload algorithmic capacity (throwing a `400 Bad Request` execution error), or once a critical asset priority sorting index is compiled, the workflow shifts directly to live human dispatch coordinators.

## Frontend Widget Integration & Security Scopes
All interactive dashboard widgets (e.g. report text fields, trigger submission controls) verify and enforce that their outgoing requests route securely through FastAPI's JWT bearer authentication headers. Unauthenticated or expired widget sessions will fail to trigger triage calculations.