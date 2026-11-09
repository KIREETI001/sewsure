# SewSure threat model (v0.1, draft)

Owner: K6 Security & Privacy. Approver: Kireeti (A1). Date: 2026-11-01.
Companion documents: [data-inventory.md](data-inventory.md), [pilot-privacy-checklist.md](pilot-privacy-checklist.md), [security-test-plan.md](security-test-plan.md).

## 1. Scope and how to read this

This is a design-time threat model. It covers the mobile app, the API, the AI pipeline, blob storage, the database, the CI/deploy path and the tailor marketplace. It is built from the **open pull requests**, not from `main` (which has no application code yet):

| PR | Area | Head branch | What it contributes here |
|---|---|---|---|
| #5 | K2 API scaffold | `claude/k2-api-scaffold-8e086e` | routes, owner scoping, idempotency, jobs, error shape |
| #10 | K3 AI pipeline | `claude/k3-ai-pipeline-b58a9d` | stages A-H, schema + allow-list validation, safety screen, telemetry |
| #6 | K5 infrastructure | `claude/k5-infra-ci-5a4cb4` | Bicep modules, CI, deploy workflow, runbook |
| #14 | D2 mobile intake | `claude/d2-expo-intake-9c1a30` | capture, measurements, consent toggle, local draft |
| #15 | K1 contract v1 draft | `claude/k1-contract-v1-2cf6a5` | OpenAPI, schemas (photo, measurements, user, maker request, quote) |
| #7 | D9 site and waitlist | `claude/d9-site-outreach-ff77a9` | waitlist form (not connected to a backend yet) |

Paths below are paths inside those PR branches. Until the PRs merge, treat every "implemented" as "implemented in the open PR, not yet on `main`".

**Mitigation status labels**

- **implemented**: code or configuration exists in an open PR (file named). It is not proof the control works; the matching test in the test plan is what proves it.
- **planned**: named in the blueprint, a PR comment, a runbook or a stub, but no working code.
- **missing**: no code, no stub and no plan found. Needs an owner.

Blueprint references: §11.4 (security and privacy requirements), §18.2 (rehearsals), §18.3 (gates), §10 (tailor marketplace). Project non-negotiables: root `CLAUDE.md` rules 2, 4, 5, 7, 8, 9 and `services/api/CLAUDE.md` rules on authorisation, minimal prompts and logging.

## 2. Assets

| ID | Asset | Why it matters | Where it lives (design) | Sensitivity |
|---|---|---|---|---|
| A1 | Garment photos (front, back, detail) and inspiration photos | Can contain faces, rooms, other people, location metadata (EXIF), brand marks. Previews derive from them. | Phone, then private blob `uploads/` (K5 `storage.bicep`) | High |
| A2 | Body measurements (self-reported) and the saved body profile | Personal and health-adjacent; needs explicit consent, edit and delete (§11.4). | Phone draft, then Postgres (not yet modelled in the API) | High |
| A3 | Garment measurements | Low sensitivity alone; linkable to a person when combined with A2 or A1. | Same as A2 | Medium |
| A4 | Tailor briefs, maker requests and quotes | Contain a consent-filtered subset of A1/A2 plus the user's request text; quotes carry tailor prices. | Postgres, blob `exports/` | High (briefs), Medium (quotes) |
| A5 | Model keys, endpoints, cloud identities, Key Vault contents, deploy credentials | Abuse = cost burn, data exposure, impersonation. | Key Vault, managed identity, GitHub environment `staging` (OIDC) | Critical |
| A6 | Design revisions, checks and state | Integrity matters more than secrecy: a forged `PASS_SUPPORTED_CHECKS` would reach a "safe to cut" screen (rule 5). | Postgres `design_revisions` | High (integrity) |
| A7 | Account identity: user ID, role, tokens, consent record | Role decides tailor-only routes; consent record is the legal basis for A2/A4. | Not built (auth is a seam in PR #5) | High |
| A8 | Waitlist and outreach data (name, email, role, area) | Direct identifiers. | Not stored yet (PR #7 form is not connected) | Medium |
| A9 | Logs and telemetry (App Insights, Log Analytics, container logs) | Easy place for A1/A2 and free text to leak. | Log Analytics, 30-day retention (K5 `monitoring.bicep`) | Medium to High |
| A10 | Research media and notes | Needs recorded consent and source permission (§11.4). | Outside the app (D7 kit) | High |
| A11 | Source code, CI config, dependency supply chain | A poisoned dependency or workflow runs with deploy rights. | GitHub | High |

## 3. Actors

| Actor | Capability / motive | Trust |
|---|---|---|
| End user (maker) | Legitimate owner of A1-A4 for their own projects. | Authenticated, owns own data only |
| Curious or malicious user | Changes IDs in URLs, replays tokens, uploads hostile files, types prompt-injection text, floods generation to burn cost. | Authenticated, untrusted input |
| Tailor | Sees only the consent-filtered brief for requests addressed to them. May try other users' projects or revisions (blueprint §18.2 rehearsal 6). | Authenticated, role `tailor`, untrusted |
| Unauthenticated internet client | Scans the public API ingress, storage endpoint and site. | None |
| Another tenant on shared Azure services | Pivots through public endpoints (Postgres, Key Vault, ACR are public in staging). | None |
| Compromised or careless team member / agent | Commits a secret, a real photo, or a weak check; over-privileged CI. | Partly trusted |
| Third-party processors | Azure AI Foundry / OpenAI models, Content Safety, Expo/EAS, Google Play. See data-inventory for what each receives. | Contractual, not controlled |
| Prompt-injected content | Text inside an inspiration prompt, a project name, or (later) text inside a photo that tries to steer the model. | Untrusted data |
| Founder (Kireeti, Narthananilaa, Delfine) | Holds Azure, Play and Expo accounts; approves releases. | Trusted, human-only actions |

## 4. Trust boundaries

```
 [Phone: app + local draft] --TLS--> [Container App: FastAPI] --managed identity--> [Postgres]
        |                                   |    |                                 [Blob: uploads/previews/exports]
        | upload ticket (short-lived)       |    +--> [AI pipeline] --> [Azure AI Foundry / Content Safety]
        +-----------------------------------+--------------------------------------> Blob (direct, scoped)
 [Tailor app session] --TLS--> same API (role = tailor)
 [GitHub Actions] --OIDC--> Azure (provision/deploy)         [Key Vault] <-- identity (Secrets User)
```

Boundaries that matter: (1) device to API; (2) API to storage and database; (3) API to the model provider; (4) user role to tailor role inside the API; (5) CI to Azure.

## 5. Threats and mitigations

IDs are stable so the test plan can reference them. STRIDE letters: S spoofing, T tampering, R repudiation, I information disclosure, D denial of service, E elevation of privilege.

### 5.1 Mobile app (PR #14)

| ID | Threat | Asset | Existing mitigation | Status | Gap / action |
|---|---|---|---|---|---|
| M1 (I) | Draft with photo paths, typed body measurements, free text and signed-in name is persisted in plain `AsyncStorage` and survives sign-out or app close. A lost or rooted phone, or a device backup, exposes it. | A1, A2, A7 | `apps/mobile/src/state/intakeStore.ts` persists under key `sewsure.intake.draft.v1`; `reset()` exists. | **missing** | No encryption at rest and no call to `reset()` outside tests (no sign-out or delete path in PR #14). Needs: sign-out and "delete my data" call `reset()`; body values not persisted unless consented; consider `expo-secure-store` for anything identifying. Owner D2/D5. |
| M2 (I) | Unticking body consent keeps previously typed body values in the persisted `measurements` map. They are not uploaded (`bodySpecs = bodyShared ? BODY_SPECS : []` in `measurements.tsx`) but stay on the device. | A2 | Upload filters by consent. | **implemented** (upload) / **missing** (local purge) | On consent withdrawal, delete body keys from the draft. Test MA-T2. |
| M3 (I) | Photos from camera or library may carry EXIF (GPS, device, timestamp). `expo-image-picker` is called with `quality: 0.8` and no explicit EXIF setting. | A1 | None verified. | **missing** | Server must strip EXIF on ingest (see B3); do not rely on the client. |
| M4 (S/E) | The client chooses `role` (`user` or `tailor`) on the entry screen (`app/index.tsx`, `intakeStore.role`). If the server ever trusted a client-sent role, anyone could become a tailor. | A7, A4 | Contract `User.role` is server-side and `createQuote` returns 403 for non-tailors (PR #15 `openapi/sewsure.v1.yaml`). | **planned** | PR #5 `CurrentUser` has only `id`; no role. Role must come from the verified token or a server-side user row. Test A-T6. Owner K2. |
| M5 (I) | Auth tokens stored insecurely when the real client arrives (today `signIn` returns a mock session). | A7 | `mockApi` marks responses `provenance: "mock"` and the UI shows a badge. | **planned** | Specify token storage (SecureStore or equivalent) before the live client is written. Owner D2/K2. |
| M6 (I) | Secrets in the app bundle. | A5 | `app.json` contains permission strings only; model keys are server-side by design (rule 7). | **implemented** (nothing found) | Keep a CI scan of the built bundle (gitleaks on source is not enough). Test S-T4. |
| M7 (T) | Deep link scheme `sewsure` (`app.json`) used to push a screen or parameters. | A6 | No deep-link handlers found in PR #14. | **implemented** (nothing to abuse yet) | Re-review when D3/D4/D5 add routes that take IDs. |
| M8 (R/I) | Consent is a toggle plus a placeholder version string `body-v0-draft`; no timestamp is sent, and the consent text key `measure.bodyConsent` is a draft. | A2, A7 | `BODY_CONSENT_VERSION` in `src/api/types.ts`; contract `Consent{consent_version, accepted_at, body_measurements, image_use, withdrawn_at}`. | **planned** | Consent text needs founder approval (needs-human). Client must send what the contract's `Consent` requires; server records `accepted_at`. |
| M9 (I) | Guest mode (`guest` flag) could keep or send data without an account. | A1, A2 | "Not uploaded (guest)" status shown. | **implemented** (UI) | Confirm the live client never uploads in guest mode. Test MA-T3. |

### 5.2 API (PR #5, contract PR #15)

| ID | Threat | Asset | Existing mitigation | Status | Gap / action |
|---|---|---|---|---|---|
| B1 (E/I) | Wrong-user access (IDOR) on project, revision, job and design routes. | A4, A6, A1-A3 | Every service lookup is owner-scoped: `get_project`, `get_job`, `get_revision` (joins `Project.owner_id`) in `services/api/sewsure_api/services.py`; misses return 404 via `errors.NotFound`, so existence is not leaked. `tests/test_access.py` has a route table plus `test_every_route_is_covered`, which fails when a route has no wrong-user entry. | **implemented** | Strong pattern. K6 extends it to the routes that PR #5 does not have yet (photos, measurements, consent, delete, maker requests, quotes). Tests A-T1..A-T12. |
| B2 (S) | No real authentication: `RejectAllAuth` rejects everything; tests inject `X-Test-User`. A misconfigured deploy that swaps in the test stub would let anyone act as anyone. | A7 | `auth.py` seam; default provider rejects all; stub lives only in `tests/conftest.py`. | **planned** | Real provider (JWT verification: issuer, audience, expiry, signature, clock skew) not built. Add a startup assertion that the provider is not a test stub when `SEWSURE_ENVIRONMENT != local`. Tests A-T13..A-T16. Owner K2. |
| B3 (T/D) | Upload abuse: oversize, wrong MIME, polyglot or decompression-bomb images, SVG or HTML with a spoofed image type, EXIF GPS. | A1 | Contract `PhotoRef`: allow-listed `content_type`, `byte_size` max 15,728,640, `status` `pending_upload -> uploaded -> verified/rejected`, "only verified photos may feed generation" (PR #15). OpenAPI returns 413 for too large. | **planned** (contract only) | No API route, no storage code, no magic-byte or decode check, no EXIF strip, no pixel-count cap. Tests U-T1..U-T12. Owner K2 (routes) with K6 (`services/api/security/`). |
| B4 (I) | Photo access without a scoped link: guessable blob URLs, long-lived SAS, sharing a SAS across users. | A1 | Storage is private, shared-key off, public blob access off (K5 `storage.bicep`); contract says downloads use short-lived scoped links and `storage_ref` is opaque. | **implemented** (storage) / **planned** (link issuing) | User-delegation SAS issuing is not written. Requirements: expiry in minutes, read-only, single blob, bound to the caller's ownership check. Tests U-T13..U-T15. |
| B5 (R/I) | No deletion or export path in the API or the contract: no `DELETE` route, no export route, no consent-withdraw route (`Consent.withdrawn_at` exists but nothing sets it). Blueprint §11.4 and gate G3 both require deletion. | A1-A4, A7 | None. Migration `0001_initial_schema.py` has foreign keys without `ON DELETE` rules and there is no users table. | **missing** | Contract gap (K1) then API (K2/K6). Tests D-T1..D-T12. Needs a deletion design: cascade rules, blob removal, what survives in backups and soft-delete (see §5.5). |
| B6 (D) | No rate limit, request-size cap or concurrency cap. `POST /v1/projects/{id}/generate` triggers paid model work. Contract lists a 429 but the app never returns one. | A5 (cost), A9 | Idempotency keys stop duplicate jobs for the same key (`idempotent_create`), job `max_attempts`. | **missing** | Per-user and global limits, body size cap, max `inspiration` size. `GenerateRequest.inspiration` is `dict[str, Any]` with no bound. Tests R-T1..R-T4. Owners K2 and K7 (cost). |
| B7 (I) | Free text stored and echoed: `Job.error_message` is stored verbatim and returned in `JobOut.error.message`; `fail_job(message=...)` takes any string. If a caller passes model output, user text or an exception string, it reaches the client and the logs. | A1-A3, A9 | `fail_job` validates the code format only. | **missing** | Restrict messages to a fixed table keyed by error code. Test L-T3. Owner K2/K3. |
| B8 (T) | Request parameters: user-supplied recipe parameters are validated for key pattern and value type (`validate_parameters`: `_mm` numbers 0-5000, `_count` ints, else string or bool) and for allow-listed keys (`_check_params`). String values have no length cap; level values are not checked against the recipe's levels. | A6 | `schemas.py`, `services.py` in PR #5. | **implemented** (type and key) / **missing** (string length, level membership) | Add `maxLength` and level membership via the feasibility seam. Owner K2/N1. |
| B9 (E) | Design state forged or upgraded by a caller. | A6 | State comes only from `FeasibilityChecker.evaluate`; the API stores it. No request schema has a `status` field (`DesignCreate`, `RevisionCreate` use `extra="forbid"` where set). `UnconfiguredFeasibility` makes every recipe unknown, so nothing can pass. | **implemented** | `DesignCreate` does not set `extra="forbid"`; unknown fields such as `status` are silently ignored today (safe, but add the forbid). Test T-T1..T-T3. |
| B10 (T) | Concurrent or replayed edits create inconsistent revisions. | A6 | Compare-and-set on `superseded_by_revision_id`; unique `(design_id, revision_number)`; idempotency records scoped by owner, scope and key. | **implemented** | Covered by K2 tests; K6 adds cross-user idempotency-key reuse (A-T10). |
| B11 (I) | API self-description and errors leak internals: FastAPI `/docs`, `/redoc`, `/openapi.json` are on by default; default 500 handler; no request ID in errors. | A9 | Custom `ApiError` shape for HTTP and validation errors (`app.py`). | **missing** (docs off in non-local) | Disable docs outside local; generic 500 handler; populate `request_id`. Test H-T1..H-T3. |
| B12 (I) | Missing browser-facing headers and CORS policy. The mobile app does not need CORS, so the safe default is none. | A7 | None. | **missing** | Explicit CORS deny; `X-Content-Type-Options`; HSTS at ingress. Low priority for a mobile-only API. |
| B13 (I) | Database runs as the Entra **administrator** identity (`POSTGRES_USER` = the shared identity, K5 `postgres.bicep`); a SQL injection or code-exec bug would have admin rights. SQLAlchemy ORM is used with bound parameters. | A1-A4 | Password auth disabled; Entra only; ORM. | **implemented** (auth) / **planned** (least privilege) | Runbook step 8 mentions a "database role"; confirm it creates a non-admin application role and that the API uses it. Owner K5. |

### 5.3 AI pipeline (PR #10)

| ID | Threat | Asset | Existing mitigation | Status | Gap / action |
|---|---|---|---|---|---|
| P1 (T/E) | Prompt injection in the inspiration text tries to make the model output geometry, new recipe IDs, a "pass" state, or hidden instructions. | A6 | Defence in depth: (1) screen before the model (`ai/safety.py`); (2) system prompts treat input as untrusted data (`ai/prompts/stage_b_v0.md`, `stage_d_v0.md`); (3) JSON schema validation with `additionalProperties: false` and an enum-only stage B schema (`ai/schemas.py`); (4) `validate_candidates` rejects any recipe ID, parameter name or level outside `RECIPE_ALLOW_LIST` and fails closed; (5) design state comes only from the feasibility port, which maps anything outside the five states to `FAILED_CHECKS` (`ai/feasibility_port.py`). | **implemented** | The allow-list and engine are what actually protect; the prompt wording is not a control. Tests I-T1..I-T10 drive hostile model outputs through `MockModelClient(scripted=...)`. |
| P2 (T) | The screen is bypassable. `MockSafetyScreen` is eight regexes; it is explicitly "NOT evidence of Prompt Shields detection rates". Azure Prompt Shields is a stub that raises `NotImplementedError`. | A6 | Regex screen in the mock; layers behind it still hold (P1). | **planned** (production screen) | No production screen exists. Do not claim detection rates. Pilot gate: Prompt Shields wired, or an explicit founder decision to rely on layers 3-5 only. Owner K3. |
| P3 (I) | Over-sharing to the model: prompts must carry no names, emails, raw body measurements or photo content unless a stage needs them. | A1, A2 | Only `inspiration_text` (stage B) and `attributes` plus `allowed_recipes` (stage D) go to the model; `ModelRequest.user_payload` comment says "already minimised"; `Telemetry` never stores prompts or user text. | **implemented** (today's two stages) | Nothing enforces minimisation in code. Add a payload-key allow-list check and a canary test (I-T11, I-T12). Must be revisited when K4 vision assist or image generation sends photos. |
| P4 (I) | Free-text fields other than `inspiration_text` (project `name`/`intention`, `extra_materials`, `condition_notes`, `modification_request`) later flow into prompts without screening. | A1, A6 | `screen.screen()` is called once on `inspiration_text` only. | **missing** | Screen and minimise every user-supplied string that reaches a model. Test I-T9. |
| P5 (D/cost) | Retry storms and cost burn: `MODEL_ATTEMPTS = 2`, job `max_attempts = 3`. No per-user cost cap, no request throttling. | A5 | Cost is logged per call (`log_call_summary`). Budget alerts at group level (K5 `budget.bicep`). | **planned** | Enforcement (per-user daily generation cap) belongs with B6. Owner K7 with K2. |
| P6 (T) | Image-borne injection (text in a photo) once photos reach a vision model (K4) or image generation (stage G). | A6 | Stage G today builds the concept from the validated spec only, never raw user text (`stage_g_visual_concept`). | **planned** | No photo reaches a model in PR #10. Add image-injection cases to the AI eval set before K4 ships. |
| P7 (I) | Provider-side retention of prompts (abuse monitoring) and region. | A1-A3 | None documented. | **missing** (decision) | Founder decision: confirm provider retention behaviour and region from current Microsoft documentation and record it in data-inventory §6. |
| P8 (I) | Model errors leaking input: `ModelError(code, message)` formats `code: message` into the exception text. Stages re-raise only `exc.code`, so today's path is safe. | A9 | `StageError` carries the code only. | **implemented** (today) | The real Azure client must never put request text in `ModelError.message`. Test L-T4. |
| P9 (E) | Model key exposure. | A5 | `AzureFoundryClient` reads endpoint and deployment from env, expects managed identity or Key Vault; no key in code; runbook grants `Cognitive Services OpenAI User` to the identity. | **implemented** (stub) / **planned** (real) | Re-check when the real client lands (no key in env vars or logs). Test S-T1..S-T3. |

### 5.4 Blob storage (PR #6)

| ID | Threat | Asset | Existing mitigation | Status | Gap / action |
|---|---|---|---|---|---|
| S1 (I) | Public or anonymous blob access. | A1 | `allowBlobPublicAccess: false`, `allowSharedKeyAccess: false`, containers `publicAccess: None`, `minimumTlsVersion: TLS1_2` in `infrastructure/modules/storage.bicep`. | **implemented** | Add an infra test or policy check in CI (K5) that these flags stay set. Test S-T5. |
| S2 (I) | Storage account reachable from the whole internet (`publicNetworkAccess: Enabled`). Access control is identity-only, which is acceptable for staging. | A1 | RBAC + SAS only. | **implemented** (staging) / **planned** (pilot) | Pilot decision: private endpoint or firewall rules. |
| S3 (I/R) | Deleted photos remain recoverable: blob `deleteRetentionPolicy` and container soft delete are 7 days. A user "delete" is therefore not immediate erasure. | A1 | None needed for erasure. | **implemented** (config) | The user-facing deletion promise must say this, or soft delete must be disabled for `uploads/`. Founder decision (data-inventory §5). |
| S4 (I) | Lifecycle rules delete `uploads/` after 30 days and `previews/`, `exports/` after 90 days **from last modification** (`lifecycle` resource). Raw photos tied to an active project would disappear; derived data outlives the raw photo. | A1, A4 | Lifecycle policy exists. | **implemented** (default values) | Periods are defaults, not decisions; K5 comment says "K6 to confirm". This document does **not** choose them: founder decision F-01 and F-02. |
| S5 (T) | A single shared identity has Blob Data Contributor, Key Vault Secrets User, ACR pull and database admin. Compromise of the API process reaches all of them. | A1, A5 | One user-assigned identity shared by the API app and the Job (`identity.bicep`, `containerapps.bicep`). | **implemented** (single identity) | Split identities (API vs migration Job vs future worker) before a real-user pilot. Owner K5. |
| S6 (T) | Upload ticket abuse: client uploads a different file than declared, or reuses a ticket. | A1 | Contract: ticket is short-lived and the server verifies MIME, size and content afterwards. | **planned** | Post-upload verification job must read the blob with a size and decode limit and set `verified` or `rejected`; unverified blobs are never served or sent to a model. Tests U-T5..U-T10. |

### 5.5 Database, logs and backups

| ID | Threat | Asset | Existing mitigation | Status | Gap / action |
|---|---|---|---|---|---|
| D1 (I) | Public database endpoint with `AllowAzureServices` (0.0.0.0) firewall rule; any Azure tenant's workload can reach the endpoint (auth still required). | A2, A4 | Entra-only auth, password auth disabled (`postgres.bicep`); file comments "Staging only; replace with VNet integration or a private endpoint before any real-user pilot". | **implemented** (staging) / **planned** (pilot) | Pilot blocker, tracked in the checklist (C-INF-3). |
| D2 (I/R) | Backups keep deleted rows for `backupRetentionDays: 7`. Account deletion is complete in the live database but not in backups for up to 7 days. | A2, A4 | Short, fixed backup window. | **implemented** (config) | State this in the privacy notice. |
| D3 (I) | Logs capture bodies, tokens or photo paths. Container Apps console logs and App Insights collect whatever the app prints. | A9 | `services/api/CLAUDE.md` forbids logging photos, tokens or body measurements; AI telemetry stores no prompts; `monitoring.bicep` caps ingestion at 1 GB/day and keeps 30 days. | **planned** (rule only) | No redaction filter and no log test. Tests L-T1..L-T5. K7 owns telemetry; K6 owns the redaction filter in `services/api/security/`. |
| D4 (T) | Log or telemetry injection (newline or control characters in user text) forging log lines. | A9 | None. | **missing** | Structured logging with escaped fields; no user text in log messages. |

### 5.6 Tailor marketplace (contract PR #15; K8 backend not started)

| ID | Threat | Asset | Existing mitigation | Status | Gap / action |
|---|---|---|---|---|---|
| T1 (I) | Tailor sees data beyond what the user consented to (full profile, other photos, other revisions). | A2, A4, A1 | Contract `TailorBrief` is the only object a tailor receives; it lists `shared_photo_ids`, `shared_measurements` (only ticked dimensions) and a `consent` block (`consent_version`, `shared_fields`, `consented_at`). `MakerRequestCreate` makes the server build the brief from the revision and the selected keys. | **planned** (contract) | No tailor read route exists in the contract (only `POST /v1/maker-requests` and `POST .../quotes`). Server-side filtering must be tested with a canary field. Tests M-T1..M-T8. Owner K8. |
| T2 (E) | Tailor uses another project or revision ID (blueprint §18.2 rehearsal 6). | A4, A6 | Pattern from B1 (owner-scoped lookups, 404). | **planned** | Needs a tailor-scoped access rule: a tailor may read only requests addressed to them. Tests M-T2, M-T3. |
| T3 (E) | A user (non-tailor) submits a quote, or a tailor edits a request. | A4 | Contract defines 403 for non-tailors on `createQuote`. | **planned** | Role not available in `CurrentUser` yet (M4). Tests M-T4. |
| T4 (T) | Brief says `verified_checks` for a design that did not pass; or the brief is built from a stale revision. | A6, A4 | Contract `allOf`: `verified_checks` requires `design_status = PASS_SUPPORTED_CHECKS`; request references one frozen revision. | **planned** (schema) | Server must derive the label from the stored state, never from the client. Test M-T5, M-T6. |
| T5 (I/R) | Consent withdrawal does not reach tailors: user revokes but the tailor still holds the brief or photos. | A4 | `WITHDRAWN` status exists; `Consent.withdrawn_at` exists. | **planned** | Define what withdrawal does to an already-delivered brief and shared photo links (links must expire or be revoked). Founder decision F-07. |
| T6 (S) | Fake or impersonating tailor profiles; abuse of contact channels. | A4, A7 | None (no tailor vetting or onboarding spec). | **missing** | Pilot: tailors are recruited by name by a founder (needs-human) and enabled manually. No open registration. |
| T7 (I) | Free text in quotes and requests (1000 chars) used for phishing, off-platform payment requests or harassment. | A7 | No payment code by rule; contract forbids fund transfer. | **missing** | Add a report/removal path and a visible warning; out-of-scope for payments. Founder decision. |

### 5.7 CI, supply chain and secrets

| ID | Threat | Asset | Existing mitigation | Status | Gap / action |
|---|---|---|---|---|---|
| C1 (I) | Secret, real photo or body data committed. | A5, A1, A2 | `.claude/hooks/guard-paths.mjs` blocks edits to secrets, keystores and `infrastructure/prod/`; `.gitignore` for `.env`; `.env.example` has a placeholder only. | **implemented** (edit-time guard) | No repository-level scanner in CI: `.github/workflows/ci-python.yml` has ruff, pyright and pytest only. gitleaks, Bandit, pip-audit and dependency review are required by K6's definition of done and are **missing** from CI. Owner K5. |
| C2 (T) | CI/deploy compromise. | A5 | OIDC federated login, no stored Azure secrets; `deploy-staging.yml` runs on `workflow_dispatch` only, in GitHub environment `staging`, `permissions: id-token: write, contents: read`. | **implemented** | Runbook says "add a required reviewer in GitHub" (needs-human). Actions are pinned by major tag (`@v4`, `@v2`), not commit SHA. |
| C3 (T) | Poisoned or vulnerable dependency (Python, npm). | A11 | Lock files in PR #5 (`uv.lock`) and PR #14 (`package-lock.json`). | **implemented** (locks) | Add `pip-audit`, `npm audit` and Dependabot. |
| C4 (I) | Test fixtures contain real people. | A1, A2 | Rule 7; D2 fixtures are synthetic (`file:///synthetic.jpg`); contract fixtures are generated by `build_fixtures.py`. | **implemented** | Add a fixture scan (image EXIF/face check is not automatable; use a reviewer checklist item). |
| C5 (R) | Waitlist data collected without a basis. | A8 | PR #7 form is not connected; `privacy.html` states retention is "to be set by the founders". | **implemented** (nothing stored) | Before connecting a backend: retention period (F-09), deletion contact, storage location. |

## 6. What the API will not leak by design (properties to keep)

1. A miss and a wrong-user hit are indistinguishable (404, not 403).
2. Design state is a stored engine output; no request field sets it.
3. The model's output is untrusted and is validated twice (shape, then allow-list).
4. Storage is identity-only; no shared key, no public blob URL.

Each of these has a test in the test plan so a refactor cannot silently remove it.

## 7. Top risks for a first pilot (ranked)

1. **No deletion, export or consent-withdrawal path** (B5). Blocks G3 by its own wording ("No user consent, deletion policy or working recovery").
2. **No real authentication or role** (B2, M4). Everything else assumes it.
3. **Upload pipeline does not exist** (B3, B4, S6): no validation, no EXIF strip, no scoped links.
4. **Tailor access is contract-only** (T1-T3): the brief filter is the main privacy promise to users.
5. **Logs and error messages can carry personal data** (B7, D3).
6. **Local draft in plain storage with no purge** (M1, M2).
7. **Public Postgres/Key Vault/ACR endpoints and one over-privileged identity** (D1, S5): acceptable for staging only.
8. **No secret/dependency scanning in CI** (C1).
9. **No cost throttle on generation** (B6, P5).
10. **Mock-only safety screen** (P2).

## 8. Needs other PR

| # | Gap | File / PR | Owning agent | Why it matters |
|---|---|---|---|---|
| N-1 | No `DELETE` project/garment/photo, account erase, data export, or consent-withdraw routes in the contract. `Consent.withdrawn_at` has no writer. | `packages/contracts/openapi/sewsure.v1.yaml` (PR #15) | K1 | B5, gate G3, blueprint screen 10 (delete/export) |
| N-2 | No tailor-side read routes (list requests addressed to me, read brief), tailor profile or directory routes, request withdraw route, or photo download (scoped link) route. | same | K1, K8 | T1-T3 cannot be tested or built without them |
| N-3 | `CurrentUser` has no role or consent state; no `users` table. | `services/api/sewsure_api/auth.py`, `models.py` (PR #5) | K2 | M4, T3, consent record |
| N-4 | Foreign keys have no `ON DELETE` rule; deletion cascade is undefined. | `services/api/migrations/versions/0001_initial_schema.py` (PR #5) | K2 | B5 |
| N-5 | `Job.error_message` is free text returned to clients. | `services/api/sewsure_api/services.py` `fail_job`, `schemas.py` `JobOut` (PR #5) | K2 with K3 | B7 |
| N-6 | `GenerateRequest.inspiration` is an unbounded `dict[str, Any]`; no body-size cap; no rate limit. | `services/api/sewsure_api/schemas.py`, `app.py` (PR #5) | K2 | B6 |
| N-7 | `DesignCreate` does not forbid extra fields; parameter string values have no length cap and levels are not checked against the recipe. | `services/api/sewsure_api/schemas.py` (PR #5) | K2 with N1 | B8, B9 |
| N-8 | `/docs`, `/redoc`, `/openapi.json` enabled for all environments; no generic 500 handler; `request_id` never populated. | `services/api/sewsure_api/app.py` (PR #5) | K2 | B11 |
| N-9 | No startup guard that the auth provider is a real one outside `local`. | `services/api/sewsure_api/app.py` (PR #5) | K2 | B2 |
| N-10 | Only `inspiration_text` is screened; other user strings are not. Payload minimisation is by convention, not enforced. | `services/api/ai/pipeline.py`, `model_client.py` (PR #10) | K3 | P3, P4 |
| N-11 | `MockSafetyScreen` is the only screen; Prompt Shields is a stub. | `services/api/ai/safety.py` (PR #10) | K3 (human: create the Azure resource) | P2 |
| N-12 | CI has no gitleaks, Bandit, pip-audit, npm audit or dependency-review job. | `.github/workflows/ci-python.yml`, `ci-mobile.yml` (PR #6) | K5 | C1, C3 |
| N-13 | Single shared identity is also Postgres admin; public endpoints on Postgres, Key Vault, ACR, storage; `AllowAzureServices` firewall rule. Acceptable for staging only. | `infrastructure/modules/*.bicep` (PR #6) | K5 | D1, S2, S5 |
| N-14 | Retention values in Bicep (30 and 90 days) and soft delete (7 days) are defaults waiting on a founder decision. | `infrastructure/modules/storage.bicep` (PR #6) | K5 (after founder decision) | S3, S4 |
| N-15 | Draft store is plain AsyncStorage; no sign-out or delete path calls `reset()`; body keys survive consent withdrawal; consent version is a placeholder with no timestamp. | `apps/mobile/src/state/intakeStore.ts`, `app/(intake)/measurements.tsx` (PR #14) | D2, D5 | M1, M2, M8 |
| N-16 | Waitlist form is not connected; when it is, it needs a storage decision, retention and a deletion route. | `apps/site/assets/join.js`, `apps/site/privacy.html` (PR #7) | D9 | C5 |

## 9. needs-human (for L0)

- Approve consent text and version for body measurements, image use and tailor sharing (Narthananilaa for content, Kireeti for legal posture, Delfine for plain language).
- Decide the retention periods F-01..F-10 in [data-inventory.md](data-inventory.md).
- Create the Azure AI Content Safety resource if Prompt Shields is to be used (Kireeti).
- Add a required reviewer to the GitHub environment `staging` (Kireeti).
- Decide how pilot tailors are recruited and enabled, and who can contact them.
- Confirm model provider data-handling terms and region from current vendor documentation.

## 10. Review and change

Re-run this model when any of these change: a new route, a new data field, a new model stage that receives photos, a new third-party processor, or the tailor read path. Each change should add or update a threat row and a test row in the same PR.
