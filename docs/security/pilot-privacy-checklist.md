# Pilot privacy checklist (v0.1, draft)

Owner: K6. Approver: Kireeti. Date: 2026-11-01.
Basis: blueprint §11.4 (security and privacy), §18.2 rehearsals 2, 3 and 6, §18.3 gate **G3 - external pilot**, whose blocking condition is "No user consent, deletion policy or working recovery" and whose unblocking evidence is "Approved participant protocol and access tests".

**Rule:** no real user, tailor or research participant receives a build until every **BLOCKING** item is `pass` with evidence linked in the pilot-build PR. A `fail` or `n/a without reason` blocks. K6 runs the checklist before every pilot build and attaches the filled copy to the PR. Status today (2026-11-01): all items are `not run` because no pilot build exists; the "Today" column shows what the open PRs imply.

Evidence types: T = automated test (id from [security-test-plan.md](security-test-plan.md)), S = screenshot or API trace, D = signed or dated document, H = human confirmation by a named person.

## A. Consent and protocol (gate G3 wording)

| ID | Check | Blocking | Evidence | Today |
|---|---|---|---|---|
| C-CON-1 | Participant protocol approved (research consent form, information sheet, supervisor/ethics review as required by NTU). | Yes | D (approval record) | Open: D7 item H-05 |
| C-CON-2 | Consent text for body measurements, image use (`app_only`/`research`/`research_and_demo`) and tailor sharing is approved and versioned; `BODY_CONSENT_VERSION` is no longer `body-v0-draft`. | Yes | D + S of screen | Placeholder in PR #14 |
| C-CON-3 | Consent is opt-in, separate for body data, image use and tailor sharing; body-measurement screen works fully with body consent off. | Yes | T MA-T1, S | UI toggle exists (PR #14) |
| C-CON-4 | Server stores `consent_version` and `accepted_at` for each consent and rejects body-profile writes without it. | Yes | T D-T9, A-T11 | Missing (no users table) |
| C-CON-5 | Withdrawing consent stops sharing and removes the body profile; the app also purges local body values. | Yes | T D-T7, MA-T2, S | Missing |
| C-CON-6 | Participants under the age the protocol allows are excluded at enrolment (protocol states the rule). | Yes | D, H | Decision pending (F-13) |
| C-CON-7 | Privacy notice is published, plain language, states what is collected, who sees it, retention periods (from the F-xx decisions), delete route, and that backups and soft-delete copies expire after a stated time. | Yes | D, S | Site privacy page has placeholders (PR #7) |

## B. Deletion, correction, export (blueprint §11.4)

| ID | Check | Blocking | Evidence | Today |
|---|---|---|---|---|
| C-DEL-1 | In-app "delete this photo", "delete this project" and "delete my account and data" exist and work end to end. | Yes | T D-T1..D-T6, S | Missing (no routes) |
| C-DEL-2 | After account deletion no row or blob remains for that user in the live database or storage (verified by query and listing). | Yes | T D-T6, D-T8 | Missing |
| C-DEL-3 | Remaining copies (backups 7 days, blob soft delete 7 days, logs 30 days: current config) are documented with their expiry and match the privacy notice; or soft delete is disabled by decision F-01. | Yes | D | Config exists; decision open |
| C-DEL-4 | Correction path: user can edit or replace each measurement; edits create a new revision and invalidate downstream plans (root rule 3). | Yes | T D-T10 | Contract has PUT measurements |
| C-DEL-5 | Export of the user's data (blueprint screen 10) returns only the caller's data. | Yes if promised in the app, otherwise remove the promise | T D-T11, A-T12 | Missing |
| C-DEL-6 | A named contact and a response time exist for deletion requests that bypass the app (email). | Yes | D, H | Site copy has a placeholder |
| C-DEL-7 | Retention periods F-01..F-10 are decided by the founders and implemented in Bicep and code. | Yes | D (decision record), T S-T6 | Open |

## C. Access control

| ID | Check | Blocking | Evidence | Today |
|---|---|---|---|---|
| C-ACC-1 | `test_every_route_is_covered`-style test passes: every route has an owner/wrong-user/anonymous case. | Yes | T A-T1..A-T12 | Implemented for PR #5 routes only |
| C-ACC-2 | Tailor session using another project, revision or request ID is denied (§18.2 rehearsal 6). | Yes | T M-T2, M-T3 | Missing |
| C-ACC-3 | Tailor sees only the consent-filtered brief; a canary field outside `shared_*` never appears. | Yes | T M-T1 | Missing |
| C-ACC-4 | Real authentication in place; test stub cannot be enabled outside `local`; token validation tests pass. | Yes | T A-T13..A-T16 | Seam only |
| C-ACC-5 | Role is derived server-side; a client-claimed role is ignored. | Yes | T A-T6 | Missing |
| C-ACC-6 | Wrong-user access returns 404 and the same body as a non-existent ID. | Yes | T A-T3 | Implemented in PR #5 |

## D. Uploads and photos

| ID | Check | Blocking | Evidence | Today |
|---|---|---|---|---|
| C-UPL-1 | Size cap, MIME allow-list and content (magic-byte + decode) checks enforced; only `verified` photos feed generation or overlays. | Yes | T U-T1..U-T12 | Contract only |
| C-UPL-2 | EXIF/GPS removed before storage or any model call. | Yes | T U-T11 | Missing |
| C-UPL-3 | Photos live in private storage; no public URL; download links are short-lived and owner-bound. | Yes | T U-T13..U-T15, S-T5 | Storage private (PR #6); links missing |
| C-UPL-4 | Content safety screening of uploads is on, or a founder-signed decision documents why not for this pilot. | Yes | D/H | Not wired |
| C-UPL-5 | Weak-network upload retries without duplicate projects (§18.2 rehearsal 2). | Yes | T (K2 idempotency) + S | Idempotency implemented (PR #5) |

## E. AI pipeline

| ID | Check | Blocking | Evidence | Today |
|---|---|---|---|---|
| C-AI-1 | Prompt-injection suite passes: no invented recipe ID, parameter, level or geometry reaches a stored revision; state never set by the model. | Yes | T I-T1..I-T10 | Layers implemented (PR #10); tests to write |
| C-AI-2 | Only the minimum fields reach the model; canary names/emails/body values never appear in a `ModelRequest`. | Yes | T I-T11, I-T12 | Convention only |
| C-AI-3 | Production safety screen is wired, or a founder-signed decision states reliance on the allow-list layers alone. No detection-rate claim without a measured denominator. | Yes | D/H | Mock only |
| C-AI-4 | Model credentials only in Key Vault or managed identity; none in app, repo, logs or env dumps. | Yes | T S-T1..S-T4 | Stub reads env endpoint only |
| C-AI-5 | Provider data-handling terms and region read from current vendor documentation and recorded (F-11); consent text matches. | Yes | D | Unverified |
| C-AI-6 | Per-user and global generation limits and the Azure budget alerts are on; model timeout fails the job safely and the draft stays recoverable (§18.2 rehearsal 3). | Yes | T R-T1..R-T4, S | Alerts defined (PR #6); limits missing |
| C-AI-7 | Unverified or model-only images never reach a "safe to cut" screen; previews labelled approximate (root rule 5). | Yes | T T-T1..T-T3, S | Design state from engine only (implemented) |

## F. Logs, errors, secrets

| ID | Check | Blocking | Evidence | Today |
|---|---|---|---|---|
| C-LOG-1 | Log redaction test passes: canary email, token, body value and photo path never appear in captured logs or error responses. | Yes | T L-T1..L-T5 | Rule only |
| C-LOG-2 | Job error messages come from a fixed table. | Yes | T L-T3 | Free text today |
| C-LOG-3 | `/docs` and `/openapi.json` disabled in the pilot environment; generic 500; `request_id` present. | Yes | T H-T1..H-T3 | Open |
| C-SEC-1 | gitleaks, Bandit, pip-audit and npm audit clean in CI on the pilot commit. | Yes | S (CI run) | Not in CI |
| C-SEC-2 | No secret in the built APK/bundle (scan of the artifact, not the source). | Yes | T S-T4 | Not run |
| C-SEC-3 | Test, research and demo data are separated; no real photos or body data in the repo or fixtures; source permissions tracked. | Yes | H (reviewer checklist) | Synthetic fixtures (PRs #14, #15) |

## G. Infrastructure for a real-user pilot

| ID | Check | Blocking | Evidence | Today |
|---|---|---|---|---|
| C-INF-1 | Pilot runs in its own environment, not the staging resource group. | Yes | S | Staging only |
| C-INF-2 | Storage: public access off, shared key off, TLS 1.2 (verified on the deployed account, not just in Bicep). | Yes | T S-T5, S | Bicep sets it |
| C-INF-3 | Postgres: `AllowAzureServices` (0.0.0.0) rule removed; private endpoint or VNet; application role is not admin. | Yes | S | Staging-only config (PR #6) |
| C-INF-4 | Key Vault and registry network exposure reviewed; purge protection decision recorded. | Yes | H | Public, protection off |
| C-INF-5 | API and migration job use separate identities with least privilege. | Yes | S | Shared identity |
| C-INF-6 | Required reviewer on the `staging`/pilot GitHub environment; deploy actions pinned. | Yes | S | Runbook step, needs-human |
| C-INF-7 | Subscription-level budget set and model quota limits set (runbook). | Yes | S | Needs-human |

## H. Device and recovery

| ID | Check | Blocking | Evidence | Today |
|---|---|---|---|---|
| C-DEV-1 | Local draft is purged on sign-out and on account delete; body values purged on consent withdrawal. | Yes | T MA-T2, MA-T4 | Missing |
| C-DEV-2 | Camera or library permission denied shows a correction path (§18.2 rehearsal 1). | Yes | S (Maestro `permission-denied.yaml`) | Written (PR #14) |
| C-DEV-3 | Working recovery: killing the app mid-upload or mid-job leaves a recoverable draft and a clear status. | Yes | S, T | Offline draft flow in PR #14; server recovery to test |
| C-DEV-4 | App store data-safety answers match the data inventory. | Yes | D | Needs-human |

## I. Operations

| ID | Check | Blocking | Evidence | Today |
|---|---|---|---|---|
| C-OPS-1 | Incident contact and a written first-response note (who is told, within what time, for a data exposure). | Yes | D | None |
| C-OPS-2 | Production data access procedure: who may read pilot data, how access is logged and revoked. | Yes | D | None |
| C-OPS-3 | Tailors are recruited and enabled by a named founder; no open tailor registration in the pilot. | Yes | H | Not designed |
| C-OPS-4 | Claims audit by X2 on privacy wording: no "secure", "private by design" or "100% safe" absolutes, no unsupported claim. | Yes | S (X2 report) | Not run |

## J. Sign-off

| Role | Name | Date | Result |
|---|---|---|---|
| K6 runs checklist | agent K6 | | |
| Security approver | Kireeti | | |
| Content / protocol | Narthananilaa | | |
| Participant-facing wording | Delfine | | |

Anything only a human can do is tagged `needs-human` in the pilot-build PR for L0.
