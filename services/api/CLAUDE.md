# services/api

Owner: Kireeti. Agents: K2 API Builder, K3 AI Pipeline Engineer, K4 Vision Assist, K6 Security & Privacy, K7 Cost & Observability, K8 Marketplace Backend.

Python 3.12, FastAPI, Pydantic v2, SQLAlchemy + Alembic, PostgreSQL, Azure Blob (private), managed with `uv`. Lint with ruff, type-check with pyright, test with pytest.

## Rules

- Pydantic models are generated from `packages/contracts`. Do not hand-write request or response shapes.
- Feasibility is imported from `packages/feasibility` as a library. This service never computes pattern geometry or sets design state itself.
- Model calls are asynchronous jobs with states `queued | running | complete | failed` and recoverable errors. Retry only idempotent work.
- Every route authorises the caller against the owning user, project, revision or quote. Add a wrong-user test for each new route.
- Send the model only the fields it needs. No names, emails or raw body measurements in prompts unless the stage requires them.
- Prompts are versioned files under `ai/prompts/`. A prompt change needs the eval harness result in the PR.
- Log request ID, revision ID, latency, model deployment and cost. Never log photos, tokens or body measurements.
- No payment, escrow or commission code.
