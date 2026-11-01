# Security test plan (v0.1, draft)

Owner: K6. Approver: Kireeti. Date: 2026-11-01. Companion: [threat-model.md](threat-model.md), [pilot-privacy-checklist.md](pilot-privacy-checklist.md).

These are the tests K6 will implement once PR #5 (API scaffold) is merged. Nothing here is written yet and no code under `services/api/` is touched by this document. Tests go in `services/api/tests/security/`; helpers in `services/api/security/`.

## 1. Conventions

- Pytest, FastAPI `TestClient`, the fixtures from PR #5 `tests/conftest.py` (`client`, `ALICE`, `BOB`, stub auth and stub checker). Added fixture users: `CAROL` (tailor), `DAN` (second tailor), anonymous (no header).
- All data is synthetic. Image fixtures are generated in code (Pillow) or are tiny hand-built byte strings; no real photo is committed. Canary values (`CANARY_EMAIL = "canary.user@example.invalid"`, `CANARY_BODY_MM = 1234.5`, `CANARY_NAME`, `CANARY_TOKEN`) let tests grep logs, responses and model payloads.
- Wrong-user access returns **404** with the same body as a non-existent ID (never 403), per `errors.NotFound`.
- A test that cannot run yet because a route or module does not exist is marked `xfail(strict=True, reason="needs PR/issue")` and listed under "Blocked by". Never weaken an assertion to pass.
- "Expected" is the required behaviour, not a description of PR #5 as it is today.
- Test IDs are referenced by the checklist and the threat model.

Prefixes: **A** access, **U** upload, **D** deletion/consent, **I** injection, **M** marketplace, **MA** mobile (Jest/Maestro), **R** rate limits, **L** logs, **S** secrets/storage, **H** hardening, **T** design state.

## 2. Access control (threats B1, B2, M4, T2, T3)

| ID | Test name | Setup | Expected | Blocked by |
|---|---|---|---|---|
| A-T1 | `test_owner_can_access_each_route` | ALICE creates project, design, job, photo, measurements | Every route in `ROUTES` returns 2xx for ALICE | none |
| A-T2 | `test_other_user_gets_404_on_every_route` | Same resources, call as BOB | 404 on every route including the new ones (photos, measurements, consent, export, delete) | routes from N-1 |
| A-T3 | `test_wrong_user_response_identical_to_missing_id` | BOB requests ALICE's ID and a random UUID | Same status, same body, same headers apart from request ID | none |
| A-T4 | `test_anonymous_gets_401_on_every_route` | no credentials | 401 `UNAUTHENTICATED` everywhere except `/healthz` | none |
| A-T5 | `test_route_table_covers_all_routes` | enumerate `app.routes` | Fails when any route lacks an A-T2 entry (extend PR #5 `test_every_route_is_covered`) | none |
| A-T6 | `test_client_claimed_role_is_ignored` | BOB sends `role: tailor` in body, header and query when creating a profile or request | Role stays `user`; tailor-only routes still 403 | N-3 |
| A-T7 | `test_user_id_in_body_or_path_cannot_override_caller` | BOB posts `owner_id`/`user_id` = ALICE | Field rejected or ignored; created resource belongs to BOB | none |
| A-T8 | `test_child_resource_authorised_through_parent` | BOB posts to ALICE's project with his own revision ID and vice versa | 404 both ways; no cross-link rows | none |
| A-T9 | `test_job_poll_scoped_to_owner` | BOB polls ALICE's job | 404; ALICE's job unchanged | none |
| A-T10 | `test_idempotency_key_is_per_user` | ALICE and BOB use the same `Idempotency-Key` on `POST /v1/projects` | Two different projects; BOB never receives ALICE's replay | none |
| A-T11 | `test_body_profile_write_requires_recorded_consent` | PUT measurements with `body` and no stored consent | 422/403 `CONSENT_REQUIRED`; nothing stored | N-3 |
| A-T12 | `test_export_returns_only_callers_data` | ALICE and BOB each have data; BOB exports | Archive contains only BOB's IDs; ALICE canaries absent | N-1 |
| A-T13 | `test_expired_token_rejected` | Token past `exp` | 401 | real auth |
| A-T14 | `test_wrong_audience_or_issuer_rejected` | Valid signature, wrong `aud`/`iss` | 401 | real auth |
| A-T15 | `test_unsigned_or_alg_none_token_rejected` | `alg: none`, tampered payload, wrong key | 401 | real auth |
| A-T16 | `test_stub_auth_cannot_start_outside_local` | `SEWSURE_ENVIRONMENT=staging` with `StubAuth`/`RejectAllAuth` misuse | App refuses to start, or every request is 401 | N-9 |

## 3. Upload validation (threats B3, B4, M3, S6)

All use a generated 1x1 or small JPEG/PNG unless stated.

| ID | Test name | Input | Expected |
|---|---|---|---|
| U-T1 | `test_rejects_oversize_declared_size` | `byte_size` = 15,728,641 | 413 `PHOTO_TOO_LARGE`; no ticket issued |
| U-T2 | `test_rejects_oversize_actual_blob` | Declared small, uploaded blob larger than the cap | Photo `rejected`; blob deleted or quarantined |
| U-T3 | `test_rejects_unlisted_content_type` | `image/gif`, `image/svg+xml`, `text/html`, `application/pdf` | 422 at ticket request |
| U-T4 | `test_rejects_zero_and_negative_size` | `byte_size` 0, -1 | 422 |
| U-T5 | `test_rejects_mime_mismatch_with_magic_bytes` | Declared `image/jpeg`, bytes are PNG or ZIP | `rejected` |
| U-T6 | `test_rejects_html_or_script_payload_with_image_type` | HTML/JS bytes declared as JPEG | `rejected` |
| U-T7 | `test_rejects_truncated_or_corrupt_image` | Valid header, truncated body | `rejected` |
| U-T8 | `test_rejects_decompression_bomb` | Header claims > N megapixels (cap set in config) | `rejected` without allocating the full bitmap |
| U-T9 | `test_rejects_polyglot_file` | JPEG with appended archive/script | `rejected` or re-encoded so the extra bytes are gone |
| U-T10 | `test_unverified_photo_blocked_from_generation` | Photo in `pending_upload`, `uploaded`, `rejected` | `generate` refuses (422 `PHOTO_NOT_VERIFIED`); never reaches the pipeline |
| U-T11 | `test_exif_gps_stripped_on_ingest` | JPEG with EXIF GPS, device and timestamp fields | Stored/served bytes contain no EXIF GPS/device tags |
| U-T12 | `test_upload_ticket_belongs_to_caller_and_garment` | BOB asks a ticket for ALICE's garment | 404 |
| U-T13 | `test_download_link_is_short_lived_and_read_only` | Request link | Expiry <= configured minutes; permission read only; single blob |
| U-T14 | `test_download_link_denied_to_non_owner` | BOB requests ALICE's photo link | 404 |
| U-T15 | `test_download_link_for_unverified_or_deleted_photo_denied` | `rejected`, `pending_upload`, deleted | 404/410 |

Blocked by: photo routes, storage client, verification job (K2). The storage client uses an in-memory fake in tests; an Azurite-based test is optional.

## 4. Deletion, consent, correction (threats B5, M2, T5, D2)

| ID | Test name | Setup | Expected | Blocked by |
|---|---|---|---|---|
| D-T1 | `test_delete_photo_removes_record_and_blob` | ALICE deletes her photo | Record gone, blob absent from fake store, link requests 404 | N-1 |
| D-T2 | `test_delete_photo_wrong_user_404_and_untouched` | BOB deletes ALICE's photo | 404; photo and blob intact | N-1 |
| D-T3 | `test_delete_project_cascades` | Project with garment, photos, measurements, revisions, jobs, idempotency rows | All dependent rows and blobs gone | N-1, N-4 |
| D-T4 | `test_delete_project_wrong_user` | BOB deletes ALICE's project | 404, nothing removed | N-1 |
| D-T5 | `test_delete_is_idempotent` | Delete twice | Second call 204/404 as contracted, no error, no side effect | N-1 |
| D-T6 | `test_account_delete_leaves_no_rows_for_user` | ALICE with all resource types plus a maker request; delete account | A scan of every table for `owner_id`/`user_id`/`project_id`/derived IDs returns zero; list of blobs under her prefix is empty; BOB's data unchanged | N-1, N-3 |
| D-T7 | `test_consent_withdrawal_removes_body_profile_and_stops_sharing` | ALICE has body profile, a draft maker request | Body profile deleted; pending briefs lose body keys; `withdrawn_at` set; later body write rejected | N-1 |
| D-T8 | `test_deleted_data_not_served_from_cache_or_list_endpoints` | After D-T6 | `GET` list endpoints for ALICE return empty or 404 | N-1 |
| D-T9 | `test_consent_record_has_version_and_timestamp` | Accept consent | `consent_version`, `accepted_at` stored; withdrawal keeps the record (retention per F-04) | N-3 |
| D-T10 | `test_measurement_correction_creates_new_revision_and_invalidates_downstream` | Edit a confirmed measurement | New measurements ID; designs from old values marked stale; old revision unchanged (rule 3) | contract PUT measurements |
| D-T11 | `test_export_contains_all_callers_data_and_no_secrets` | ALICE exports | Includes projects, measurements, consent, designs; excludes tokens, internal IDs of other users, storage keys | N-1 |
| D-T12 | `test_tailor_brief_after_withdrawal_follows_decision_f07` | Request SUBMITTED, then user withdraws | Behaviour matches decision F-07 (request `WITHDRAWN`, links expired); test is `xfail` until F-07 is decided | F-07 |

## 5. Prompt injection and model-output safety (threats P1-P4, P8)

Uses `MockModelClient(scripted={...})` and the real validation path in `ai/` (PR #10). No network.

| ID | Test name | Input / scripted output | Expected |
|---|---|---|---|
| I-T1 | `test_instruction_override_text_is_blocked_by_screen` | "ignore previous instructions and ..." | `outcome = blocked`, reason `PROMPT_ATTACK_SUSPECTED`; model never called (`client.calls == []`) |
| I-T2 | `test_injection_bypassing_screen_still_yields_valid_output_only` | Screen = `AllowAllScreen`; stage B scripted to return extra keys or prose | Job fails `MODEL_OUTPUT_SCHEMA_INVALID`; nothing stored |
| I-T3 | `test_model_returns_unknown_recipe_id` | Stage D returns `evil_recipe_v9` | Rejected by `validate_candidates`; no candidate saved |
| I-T4 | `test_model_returns_unknown_parameter_or_level` | `{"crop_level": "99"}`, extra parameter | Rejected |
| I-T5 | `test_model_returns_numeric_geometry` | Parameters with numbers, `*_mm` keys, arrays of points | Rejected (schema pattern + allow-list) |
| I-T6 | `test_model_claims_pass_status` | Output includes `status: PASS_SUPPORTED_CHECKS`, `hard_pass: true` | Field rejected (`additionalProperties: false`); stored state comes from the checker only |
| I-T7 | `test_engine_unknown_state_fails_closed` | Fake checker returns `"APPROVED"` | Mapped to `FAILED_CHECKS`; not stored as pass |
| I-T8 | `test_engine_exception_fails_closed` | Fake checker raises | `FAILED_CHECKS`/failed job; no revision marked pass |
| I-T9 | `test_all_user_strings_are_screened_before_any_model_call` | Attack string in each free-text field that can reach a prompt (inspiration, project name, intention, extra materials, modification request) | Screen invoked for each; none reach the model. `xfail` for fields not yet screened (N-10) |
| I-T10 | `test_injection_corpus_never_changes_state_or_recipe_set` | Run the corpus (20+ synthetic attack strings, multi-language, encoded, markdown/code-fence, role-play) through the pipeline with `MockModelClient` default responder | Zero revisions with a recipe outside `RECIPE_ALLOW_LIST`; zero states not produced by the checker. Report counts with the corpus size as denominator; **do not report this as a Prompt Shields detection rate** |
| I-T11 | `test_model_request_contains_only_allow_listed_fields` | Run pipeline with canary name, email, body value, photo path in the request context | Every recorded `ModelRequest.user_payload` has keys within an allow-list per stage; canaries absent |
| I-T12 | `test_canary_pii_in_inspiration_text_policy` | Email in inspiration text | Behaviour per F-08 (strip or pass-through). Marked `xfail` until decided |
| I-T13 | `test_model_error_text_never_contains_user_input` | Mock raises `ModelError` built from the request | Job `error_message` and logs contain only the code |
| I-T14 | `test_image_text_injection_blocked` (future) | Image fixture with embedded text instructions, once photos reach a model | Same as I-T10. `xfail` until K4/stage G sends photos |

## 6. Tailor marketplace (threats T1-T4)

| ID | Test name | Setup | Expected | Blocked by |
|---|---|---|---|---|
| M-T1 | `test_tailor_brief_contains_only_consented_fields` | Revision with extra canary fields (other measurements, a body value, an unshared photo ID, user email) | Tailor response has only `TailorBrief` keys; canaries absent; `shared_measurements` limited to ticked keys | N-2 |
| M-T2 | `test_tailor_cannot_read_unaddressed_request` | Request addressed to CAROL; DAN reads | 404 | N-2 |
| M-T3 | `test_tailor_cannot_read_project_revision_or_photos_directly` | CAROL requests ALICE's project, revision, job, photo link not in her brief | 404 | N-2 |
| M-T4 | `test_non_tailor_cannot_create_quote` | BOB posts quote | 403 `FORBIDDEN` (contract) | N-3 |
| M-T5 | `test_brief_label_derived_from_stored_state` | Client sends `verified_checks` for a `FAILED_CHECKS` or `SUPERSEDED` revision | Request rejected or label downgraded server-side; brief never says `verified_checks` unless state is `PASS_SUPPORTED_CHECKS` | N-2 |
| M-T6 | `test_request_binds_to_frozen_revision` | Edit the design after submitting | Brief still reflects the old revision; request flagged stale | N-2 |
| M-T7 | `test_user_cannot_request_with_other_users_revision_or_photo` | BOB posts maker request with ALICE's `revision_id` or `shared_photo_ids` | 404 | N-2 |
| M-T8 | `test_quote_visible_only_to_requester_and_author` | Quote by CAROL on ALICE's request | ALICE and CAROL read it; BOB and DAN get 404 | N-2 |

## 7. Mobile (Jest / Maestro, owner D2 with K6 review)

| ID | Test name | Expected |
|---|---|---|
| MA-T1 | `body measurements screen works with consent off` | Upload payload has no body records and `body_consent_version = null` |
| MA-T2 | `withdrawing body consent purges body values from the persisted draft` | AsyncStorage content contains no body keys afterwards. Currently expected to fail (M2) |
| MA-T3 | `guest mode never calls uploadIntake with the live client` | No network call; status "not uploaded (guest)" |
| MA-T4 | `sign out and delete account clear the persisted draft` | `sewsure.intake.draft.v1` removed. Blocked: no sign-out UI yet |
| MA-T5 | `no secret-looking strings in the bundle` | See S-T4 |

## 8. Rate limits, cost, abuse (threats B6, P5)

| ID | Test name | Expected |
|---|---|---|
| R-T1 | `test_generate_rate_limited_per_user` | N+1th generate in the window returns 429 `RATE_LIMITED` with `retry_after_s`; other users unaffected |
| R-T2 | `test_oversize_json_body_rejected` | Body above cap returns 413/422 before parsing the `inspiration` dict |
| R-T3 | `test_inspiration_text_length_and_depth_limits` | Text > 1000 chars or nested dicts rejected |
| R-T4 | `test_duplicate_generate_with_same_key_does_not_double_enqueue` | Second call replays the first job (already in PR #5; kept as regression) |

## 9. Logs, errors and telemetry (threats B7, D3, D4, P8)

Capture logs with `caplog` plus the exporter handler; send canaries through every route and the pipeline.

| ID | Test name | Expected |
|---|---|---|
| L-T1 | `test_logs_contain_no_canary_values` | `CANARY_EMAIL`, `CANARY_BODY_MM`, `CANARY_TOKEN`, photo path never in any log record |
| L-T2 | `test_authorization_header_never_logged` | No `Authorization`, `Cookie` or signed-URL query string in logs |
| L-T3 | `test_job_error_message_comes_from_fixed_table` | `JobOut.error.message` equals the table entry for its code regardless of input |
| L-T4 | `test_exception_text_with_user_input_not_logged_or_returned` | Raise inside a route with user text in the exception; response and logs are generic |
| L-T5 | `test_log_injection_neutralised` | Newlines and control characters in user text appear escaped or absent in log lines |

## 10. Secrets and storage configuration (threats P9, S1, C1)

| ID | Test name | Expected |
|---|---|---|
| S-T1 | `test_no_model_key_in_settings_or_env_dump` | Settings repr and `/healthz` expose no key/secret fields |
| S-T2 | `test_azure_client_uses_identity_not_key` | Client construction has no `api_key` parameter path in production mode |
| S-T3 | `test_repo_has_no_secrets` | gitleaks clean (CI job); Bandit clean; pip-audit clean |
| S-T4 | `test_built_bundle_contains_no_secrets` | Scan the exported JS bundle for key patterns, endpoints with keys, `Bearer` literals |
| S-T5 | `test_storage_bicep_flags` | Parse `storage.bicep`: `allowBlobPublicAccess=false`, `allowSharedKeyAccess=false`, TLS1_2, containers `publicAccess=None` |
| S-T6 | `test_lifecycle_rules_match_decided_retention` | Bicep lifecycle days equal the values recorded in the founder decision (F-01, F-02). `xfail` until decided |

## 11. API hardening (threats B11, B12)

| ID | Test name | Expected |
|---|---|---|
| H-T1 | `test_docs_and_openapi_disabled_outside_local` | `/docs`, `/redoc`, `/openapi.json` return 404 when environment is not `local` |
| H-T2 | `test_unhandled_exception_returns_generic_500_with_request_id` | Body is the `ApiError` shape, no stack trace, no SQL |
| H-T3 | `test_security_headers_present` | `X-Content-Type-Options: nosniff` and no `Server` version detail; CORS denies foreign origins |

## 12. Design state integrity (threats B8, B9, T4)

| ID | Test name | Expected |
|---|---|---|
| T-T1 | `test_request_cannot_set_status_or_checks` | Posting `status`, `checks`, `hard_pass` to create/edit design is rejected (`extra=forbid`) or ignored; stored values come from the checker |
| T-T2 | `test_unreviewed_recipe_or_parameter_rejected` | 422 for unknown recipe or unlisted key; unitless numeric and `_mm` out of range rejected |
| T-T3 | `test_no_route_marks_unverified_image_safe_to_cut` | With photo `pending_upload`/`rejected`, no cut-plan or "safe to cut" payload is returned |

## 13. Tooling in CI (once K5 adds the jobs, N-12)

gitleaks (full history on PRs), Bandit on `services/api`, `pip-audit` per lock file, `npm audit --omit=dev` for mobile, dependency-review action, and the pytest security marker `-m security` as a required check.

## 14. Order of implementation

1. A-T1..A-T10 and T-T1..T-T3 (need only PR #5).
2. I-T1..I-T11, I-T13 (need PR #10).
3. L-T*, H-T*, R-T*, S-T1, S-T3, S-T5 (small, mostly independent).
4. U-T*, D-T*, A-T11..A-T16 as soon as the owning PRs (N-1, N-3, photo routes, real auth) land.
5. M-T* when K8's routes exist.

## 15. Not covered by tests (human)

- Penetration test of the deployed pilot environment.
- Review of the consent text and privacy notice wording.
- Device loss, shoulder-surfing and physical access.
- Provider-side behaviour (retention, abuse monitoring): confirm from vendor documents (F-11).
