# Contract changelog

Status: **DRAFT, not frozen.** Consumers may build against v1 now, but field names can still change until the freeze (target: before cross-team integration, blueprint §3.4). After the freeze, breaking changes need a `/v2` path and review from both consumers.

Every entry says what changed, why, and which consumers are affected.

## 1.0.0-draft.1 (2026-10-28)

First draft of contract v1 (K1).

**What**

- P0 records as JSON Schema 2020-12 in `schemas/`:
  - `design-state` (exactly the 5 states)
  - `project` and `garment`
  - `photo-ref` (private storage key plus a scoped upload ticket; no public URLs)
  - `measurements` (mm, `origin`, `confirmed_at`)
  - `design-candidate` and `DesignList` (0–3 items)
  - `design-revision` (immutable; `parent_revision_id`, `inputs_hash`, `recipe_id`/`recipe_version`, `checks`, `status`)
  - `cut-plan` (mm coordinates, ruler checkpoints, calibration state)
  - `job` (queued/running/complete/failed, with a recoverable `ApiError`)
  - `constraint-result` (`hard_pass`, `failure_codes`, `residuals`, `missing_dimensions`, `uncertainty_flags`, `alternatives`)
- Other records: `user` (role and consent version), `inspiration`, `fit-assessment` (§7.1), `diy-steps`, `diy-progress`, `maker-request` (consent-filtered tailor brief, §10.2 states), `quote`, `evidence-log` (§17.3), `api-error`.
- AI structured output for Stage D: `ai-candidate-proposal`. It holds only recipe IDs and parameters, with no geometry and no state.
- `openapi/sewsure.v1.yaml` (OpenAPI 3.1) covering every route in §3.4. It also adds a few small routes the screens need: `GET /v1/me`, `GET /v1/projects/{id}`, `GET`/`PATCH /v1/garments/{id}`, `GET /v1/revisions/{id}`, and `GET`/`PUT /v1/revisions/{id}/diy-progress`.
- Five mock scenarios in `fixtures/`, each with `"mock": true` and `provenance.source = "mock"`: `woven_shirt_crop_pass`, `lengthening_impossible`, `needs_input`, `idea_only`, `job_failed_no_designs`.
- Generated code:
  - Pydantic v2 models in `generated/python/sewsure_contracts` (datamodel-code-generator)
  - TypeScript types in `generated/ts/sewsure.v1.ts` (openapi-typescript)
- Scripts:
  - `scripts/validate.py`: checks the schemas, the spec, the fixtures and cross-record invariants
  - `scripts/build_fixtures.py`
  - `scripts/codegen.py`
- Contract tests: `tests/test_contract.py`, with 27 negative cases, and `tests/ts/fixtures.typecheck.ts`.

**Rules the schemas enforce** (beyond types)

- `PASS_SUPPORTED_CHECKS` requires `checks.hard_pass = true`, no failure codes, no missing dimensions, and a recipe ID and version.
- `FAILED_CHECKS` requires at least one failure code. `NEEDS_INPUT` requires at least one missing dimension. `FAILED_CHECKS`, `NEEDS_INPUT` and `IDEA_ONLY` all require `cut_plan_id = null`. `SUPERSEDED` requires `superseded_by_revision_id`.
- Recipe `parameters` may hold numbers only under keys ending in `_mm` or `_count`, so a unitless or `_cm` length is rejected. Every `geometry_mm` key ends in `_mm`.
- A `calibrated_overlay` cut plan requires `calibration.state = "calibrated"`. Otherwise the app shows the dimensioned diagram.
- `preview.approximate` is always `true`.
- A tailor brief labelled `verified_checks` must reference a `PASS_SUPPORTED_CHECKS` revision.
- A `failed` job must carry an `error`. A `complete` job must carry a `result` (which may hold zero designs).

**Conventions**

- IDs are opaque strings that look like `rev-002`.
- Timestamps use RFC 3339 in UTC.
- Money is an integer `amount_minor` plus an ISO 4217 currency.
- `inputs_hash` is the SHA-256 of the canonical JSON of `{inputs, recipe_id, recipe_version, parameters}`, with sorted keys and `,`/`:` separators. See `inputs_hash()` in `scripts/build_fixtures.py`.
- Idempotent POSTs take an `Idempotency-Key` header.

**Known limits**

- The Pydantic models do not enforce the conditional (if/then) rules above. Validate with `scripts/validate.py` (jsonschema), or rely on the feasibility engine to produce consistent records.
- Some generated TypeScript names are derived from file names (e.g. `"design-state.schema"`). Use the named aliases in `components["schemas"]`, such as `DesignState` and `DesignRevision`.
- No Schemathesis config yet: there is no running API to test against. Add it when K2 serves the spec.

**Consumers affected:** all of them, since this is the first draft.

- K2 (API): routes, request and response bodies, Pydantic models.
- K3 (AI): `ai-candidate-proposal`, `inspiration`.
- N1/N2 (feasibility): `constraint-result`, `FailureCode`, `design-revision.geometry_mm`, `cut-plan`.
- D2/D3 (mobile): TypeScript types and fixtures.
- K8 (marketplace): `maker-request`, `quote`.
- N6 (evidence): `evidence-log`.
