# Contract changelog

Status: **DRAFT, not frozen.** Consumers may build against v1 now, but field names can still change until the freeze (target: before cross-team integration, blueprint §3.4). After the freeze, breaking changes need a `/v2` path and review from both consumers.

Every entry says what changed, why, and which consumers are affected.

## 1.0.0-draft.3 (2026-11-02)

Stale revisions get a documented error and a machine-readable field. Approved by Kireeti; requested by X1's recheck of #22 (finding N1). Still DRAFT.

**What and why**

- **`stale` boolean, required on `DesignRevision` and `DesignCandidate`.** It is true when the revision's `inputs.measurements_id` is no longer the project's current `measurements_id`. Before this, clients could only find out by parsing prose, while `status`, `hard_pass` and `geometry_mm` still read as a pass.
- **409 `REVISION_STALE` on `GET /v1/revisions/{revision_id}/cut-plan`.** The route's 409 is now the `CutPlanUnavailable` response, which allows `REVISION_NOT_PASSING` (`recoverable: false`) or `REVISION_STALE` (`recoverable: true`). The status is checked first.
- **Recheck path documented.** `POST /v1/designs/{design_id}/revisions` with `parameters: {}` and a new `Idempotency-Key` reruns the engine on the current measurements.
- **Corrected the cut plan route's 200 description.** It said a SUPERSEDED revision gets a plan. It gets 409, as #22 implements and the 409 description already said.
- **`placket_end_from_shoulder` added to the shirt fixtures**, because #22 asks for this dimension. The values (700 and 680 mm) are synthetic. What the dimension should mean is still an open human decision on #22.
- **New fixture `stale_after_measurements_change`**, with an optional `cut_plan_error` field on the fixture scenario so mobile can mock the 409.
- `validate.py` now checks that a candidate's `stale` matches its revision, that `stale` matches the measurements IDs, and that no stale revision is served a plan.

**Stale is not a design state.** The five states are unchanged. `stale` is computed at read time, is not stored on the immutable revision, is not part of `inputs_hash`, and never changes `status`. A stale pass keeps `PASS_SUPPORTED_CHECKS` until the engine rechecks it. `Job.result.outcome` is unchanged too, because it summarises the original run.

**Not changed:** `diy-steps` and `diy-progress` still document only `RevisionNotPassing`. See the PR for the open question.

**Consumers affected**

- K2 (#22): set `stale` on revision and candidate responses, and use the documented 409. `stale` is required, so responses without it fail validation.
- D3 (#25): read `stale` on cards and design detail; lead with the recheck and do not present the cut mark or `geometry_mm` as current. Add `stale` to mocks.
- D4 (#24): `cutGuideAccess` must treat `stale: true` as closed, and handle 409 `REVISION_STALE` by offering the recheck. Add `stale` to mocks.
- All: fixtures gain `stale` and the placket dimension.

## 1.0.0-draft.2 (2026-10-28)

Fixes from the X1 review on PR #15, plus canonical vocabularies after the cross-PR check against N1 #12, N2 #9, K2 #5 and K3 #10. Still DRAFT.

**What and why**

- **A pass now means every hard gate ran and passed** (X1 finding 1, major). Under `hard_pass: true`, `constraint-result` now also requires:
  - at least one check, every check `pass` or `not_applicable`, and at least one `pass`;
  - every `residuals[].residual_mm >= 0`.

  Before, a `PASS_SUPPORTED_CHECKS` revision validated with a −150 mm residual, a failed check, or no checks at all.
- **AI output can no longer carry numbers or free text** (finding 2, major):
  - `ai-candidate-proposal` uses a new `AiParameters`: named levels (lower snake case) and booleans only. Keys ending `_mm`, `_cm`, `_in` or `_count` are rejected.
  - `rationale` and `idea_only_notes` are removed. This matches K3 #10, which forbids free text in model output.
  - An empty `proposals` list means the IDEA_ONLY path.
  - The recipe maps levels to mm.
- **Recipe `parameters` lengths are non-negative** (finding 2). `*_mm` values are now `LengthMm` (0–5000) instead of `SignedLengthMm`. This applies to RevisionCreate, revisions and alternatives.
- **SUPERSEDED cannot keep a cut plan unless it had passed** (finding 3, minor): a SUPERSEDED revision with `checks.hard_pass = false` must have `cut_plan_id = null`.
- **Measurements must be > 0 mm** (finding 4, minor). The new `common#/$defs/PositiveLengthMm` is used for `MeasurementValue.value_mm`.
- **Canonical garment dimension names.** The new `measurements#/$defs/GarmentDimension` enum covers:
  - `shoulder_to_hem`
  - `chest_flat_width`
  - `chest_circumference`
  - `waist_flat_width`
  - `hem_width`
  - `shoulder_width`
  - `sleeve_length`
  - `placket_end_from_shoulder`

  `Measurements.garment` and `MeasurementsInput.garment` only accept these keys. Names with unit suffixes and other spellings are rejected. Body measurement names stay open for now.
- **FailureCode additions the engine needs.** N1 #12 emits these and the old enum had no equivalent:
  - `CATEGORY_UNKNOWN`
  - `UNCONFIRMED_DIMENSION`
  - `POSSIBLE_UNIT_ERROR`
  - `NON_FINITE_VALUE`
  - `MISSING_PARAMETER`
  - `INVALID_PARAMETER`
  - `NO_POSITIVE_REMAINDER`
  - `MISSING_PROHIBITED_ZONES`

  No existing code was renamed.
- **NEEDS_INPUT may be explained by a failure code** as well as by `missing_dimensions`. N1 returns NEEDS_INPUT for implausible, conflicting or unit-error values and for an unknown material, where no dimension is absent. A NEEDS_INPUT revision now needs at least one missing dimension or at least one failure code. Implausible or conflicting dimensions should still be listed in `missing_dimensions`, so the app knows which field to ask for again.
- **`MeasurementIssue.code` `UNCONFIRMED` is renamed `UNCONFIRMED_DIMENSION`** so it matches the FailureCode.
- **Uncertainty flags are UPPER_SNAKE**, matching FailureCode and N1. They use the new `constraint-result#/$defs/UncertaintyFlag`. Fixtures now use `SIDE_SEAMS_NOT_VERIFIED`.
- **`Job.result.outcome` is required.** Its values are `designs | needs_input | no_feasible_design | unsupported | blocked | needs_confirmation`, which are the run summaries K3's pipeline produces.
  - `designs` requires at least one design id.
  - `blocked` and `needs_confirmation` require none.
  - `validate.py` checks that `designs` is used if and only if a design passed.
  - The outcome is a summary for the progress screen, not a design state.

**Kept stable on purpose** (the contract is the reference; consumers adopt it):

- Garment category `woven_shirt`, fabric family `woven`, and measurement origin `user_tape_measured`.
- Recipe ID `woven_shirt_crop_v1`, which must match `^[a-z][a-z0-9_]*_v[0-9]+$`.
- Existing FailureCode names. The engine should map to them:
  - `RECIPE_NOT_ALLOWED` → `UNSUPPORTED_RECIPE`
  - `CATEGORY_NOT_SUPPORTED` → `UNSUPPORTED_GARMENT_CATEGORY`
  - `MATERIAL_NOT_SUPPORTED` → `UNSUPPORTED_MATERIAL`
  - `DIMENSION_IMPLAUSIBLE` → `IMPLAUSIBLE_DIMENSION`
  - `UNIT_MIX_UP_SUSPECTED` → `POSSIBLE_UNIT_ERROR`
  - `MISSING_PARAM` → `MISSING_PARAMETER`
  - `FINISHED_LENGTH_EXCEEDS_AVAILABLE` → `INSUFFICIENT_LENGTH`
  - `PROHIBITED_ZONE_INTERSECTION` → `CUT_INTERSECTS_PROHIBITED_REGION`
- `ConstraintResult` shape: `residuals` is a list of `Residual` objects (not a flat dict), and `checks` and `checked_at` are required.
- Routes and field names (`revision_id`, `status`, `POST /v1/projects/{id}/generate`, `POST /v1/designs/{id}/revisions`), and supersede-only-if-passed.

**Tests:**
- 17 new negative schema cases in `tests/test_contract.py`, 6 parametrised AI-parameter rejections, and tests for the AI `rationale` field and RevisionCreate's negative-length check, plus positive tests:
  - NEEDS_INPUT explained by `IMPLAUSIBLE_DIMENSION` alone
  - a passed SUPERSEDED revision keeps its cut plan
  - an empty AI proposal list
- New invariant test for the job outcome.
- The old "needs_input without missing dimensions" case is replaced by "needs_input with no reason".

**Consumers affected**

- N1 (#12):
  - FailureCode names (mapping above)
  - flag casing
  - `Residual` objects
  - `checks` and `checked_at`
  - dimension keys (`shoulder_to_hem`, `chest_flat_width`)
  - category `woven_shirt`
  - a pass needs every gate to have run
- N2 (#9): dimension keys without `_mm`, origin `user_tape_measured`, category `woven_shirt`, and FailureCode names.
- K3 (#10):
  - `AiCandidateProposal` now matches its level-only, no-free-text design
  - recipe IDs must be `*_vN`
  - fill `Job.result.outcome`
- K2 (#5): routes and field names as above, and `Job.result.outcome`.
- D2/D3: `Job.result.outcome` for the progress screen, the `GarmentDimension` enum for the measurement form, and UPPER_SNAKE flags.

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
