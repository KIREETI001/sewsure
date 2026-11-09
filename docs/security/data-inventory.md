# SewSure data inventory (v0.1, draft)

Owner: K6. Approver: Kireeti (A1). Date: 2026-11-01. Companion: [threat-model.md](threat-model.md).

Sources: contract v1 draft (PR #15 schemas), API scaffold (PR #5), AI pipeline (PR #10), infrastructure (PR #6), mobile intake (PR #14), site (PR #7). Nothing is merged to `main`, and **no real user data exists yet**. "Planned" means the field is in the contract or a PR but no live system stores it.

## 1. Rules applied

- Lengths are stored in millimetres; every measurement keeps `origin` and `confirmed_at` (root rule 1).
- A retention period is **not** chosen in this document. Where infrastructure carries a default, it is listed as "current default (undecided)" and linked to a founder decision (F-xx, section 5).
- "Visible to" lists who can read the field through the intended design. Operators with database or portal access are listed separately in section 4.

## 2. Field inventory

Legend for "To AI model": **No** = never sent; **Derived** = a value computed from the field is sent; **Yes** = the field itself is sent. "Today" refers to the two model stages in PR #10 (B parse inspiration, D propose candidates).

### 2.1 Account and consent

| Field | Source | Stored where | Visible to | To AI model | Retention | Deletion path |
|---|---|---|---|---|---|---|
| `user_id` (opaque) | Server | Planned users table (not in PR #5; jobs and projects carry `owner_id` strings) | The user; operators | No | Undecided (F-03) | **Missing** (no account-erase route) |
| `role` (`user`/`tailor`) | Server-side (the app also lets the user pick one on entry; the server must not trust it) | Planned | The user; API authorisation | No | With account | Missing |
| `display_name` (max 80) | User | Planned | The user; a tailor only if the brief includes it (contract brief has no name field) | No | With account | Missing |
| Sign-in identity (email or provider ID) | Auth provider | Not designed (auth is a seam in PR #5) | Provider; operators | No | Undecided (F-03) | Missing |
| `Consent`: `consent_version`, `accepted_at`, `body_measurements`, `image_use`, `withdrawn_at` | User action | Planned | The user; operators | No | Keep as long as the data it covers exists, plus an audit period (F-04) | Withdrawal route missing |
| Mobile role / guest / signed-in name | App | Phone `AsyncStorage`, key `sewsure.intake.draft.v1` (unencrypted) | Anyone with device access | No | Until reset; no purge path today | `reset()` exists but nothing calls it outside tests |

### 2.2 Photos

| Field | Source | Stored where | Visible to | To AI model | Retention | Deletion path |
|---|---|---|---|---|---|---|
| Garment photos (front, back, detail) | Camera or library | Phone cache and draft URI; blob `uploads/` (private) | The owner; the API; a tailor only for `shared_photo_ids` in a brief | **Not today**. Planned for K4 vision assist and possibly stage G; needs a new row here first | Current default (undecided): `uploads/` blobs auto-delete 30 days after last modification (F-01). Soft delete keeps removed blobs 7 days | Missing (no photo delete route). Lifecycle rule is the only removal |
| Inspiration photo | Library | Phone draft URI; blob (`view = inspiration`) | Owner | Not today | As above | Missing |
| Photo metadata: `byte_size`, `width_px`, `height_px`, `content_type`, `status`, `has_calibration_marker`, `image_use_consent` | Server | Postgres (planned) | Owner | No | With the photo record | With the photo |
| EXIF (GPS, device, time) embedded in the file | Phone | Inside the image | Whoever can read the blob | Would be sent with the image if a photo is ever sent | Same as photo | **Strip on ingest (missing)** |
| Previews and renders derived from photos | Server | Blob `previews/` | Owner; tailor if shared | Output of stage G in future | Current default (undecided): 90 days after last modification (F-02) | Missing |

### 2.3 Measurements

| Field | Source | Stored where | Visible to | To AI model | Retention | Deletion path |
|---|---|---|---|---|---|---|
| Garment dimensions (`shoulder_to_hem`, `chest_flat_width`, ... in mm, with `origin`, `confirmed_at`, `entered_unit`, `note` max 200) | User | Phone draft; Postgres `Measurements` (planned) | Owner; tailor only for ticked keys | **Derived**: stage C receives dimension **names** only, never values (`provided_dimensions`); values go to the feasibility engine, not the model | Project lifetime (F-05) | Missing |
| Body measurements and profile (`BodyMeasurements`: `body_profile_id`, `consent_version`, values in mm) | User, opt-in | Phone draft (persists even after consent is withdrawn, M2); Postgres (planned) | Owner only. Never to a tailor as a profile (risk register: "no shared raw profiles"); only ticked keys inside a brief | **No** (rule: no raw body measurements in prompts unless a stage needs them; no stage does) | Until user deletes or consent is withdrawn, plus backup tail (F-06) | Missing |
| `note` free text on a measurement | User | Same | Owner | No | Same | Missing |

### 2.4 Projects, designs, jobs

| Field | Source | Stored where | Visible to | To AI model | Retention | Deletion path |
|---|---|---|---|---|---|---|
| Project `name` (max 200), `intention` (max 2000); contract `title` (max 120) | User | Postgres `projects` | Owner | Not today; if used in a prompt later it must be screened (P4) | Project lifetime (F-05) | Missing |
| Garment `category`, `fabric_family`, `visible_features`, `condition_notes` (max 500) | User / vision suggestion | Postgres (planned) | Owner; tailor sees category | Category and fabric family: **Yes** (pipeline stages A and C). Notes: no | Project lifetime | Missing |
| Inspiration text (max 1000), `requested_features`, `skill_level`, `tools`, `supplies` | User | Request body; job payload (contract); not persisted in PR #5 | Owner | **Yes**: `inspiration_text` goes to stage B (screened first). Parsed enums go to stage D | Undecided whether the raw text is kept after the job (F-08) | Missing |
| `extra_materials` free text (app) | User | Phone draft; request | Owner | No | Same as inspiration | Missing |
| Design revisions: `recipe_id`, `parameters`, `geometry_mm`, `checks`, `status`, `inputs_hash`, parent link | Engine/API | Postgres `design_revisions` | Owner; tailor for the frozen revision in a request | Recipe IDs and levels are model **output**, not input. Allow-listed | Project lifetime (F-05) | Missing; FKs lack `ON DELETE` |
| Jobs: `kind`, `status`, `attempts`, `error_code`, `error_message`, `stage`, `result_*` | API | Postgres `jobs` | Owner | No | Undecided (F-08) | Missing |
| Idempotency records: `owner_id`, `scope`, `key`, `request_hash`, `resource_id` | API | Postgres | Operators | No | Undecided (F-08); can be short | Missing |
| DIY progress: step status, `measured_mm`, `checked_at` | User | Postgres (planned) | Owner | No | Project lifetime | Missing |
| Evidence-log entries (`predicted_mm`, `actual_mm`, `anonymous`, `media_consent`, notes) | Team / participants | Repo or evaluation store (not the app database) | Team | No | Per research protocol (F-10) | Per protocol |

### 2.5 Tailor marketplace

| Field | Source | Stored where | Visible to | To AI model | Retention | Deletion path |
|---|---|---|---|---|---|---|
| Tailor profile (`profile_ref`, directory fields) | Tailor | Planned (K8) | Users browsing the directory | No | While the tailor is enrolled (F-03) | Missing |
| Maker request: `tailor_id`, `revision_id`, `modification_request` (max 1000), status | User | Postgres (planned) | User; the addressed tailor | No | Undecided (F-07) | Withdraw status exists; erase missing |
| Tailor brief: `verification_label`, `design_status`, category, `shared_photo_ids`, `shared_measurements` (ticked keys, mm), `unresolved_checks`, consent block | Server, from user selection | Postgres; possibly blob `exports/` | The addressed tailor and the user | No | Current default (undecided): `exports/` 90 days (F-02); DB rows undecided (F-07) | Missing. Tailor-held copies cannot be recalled (F-07) |
| Quote: `kind`, `price`, `estimated_duration_days`, `message` (max 1000) | Tailor | Postgres (planned) | The tailor; the requesting user | No | Undecided (F-07) | Missing |

### 2.6 Telemetry, logs, website, research

| Field | Source | Stored where | Visible to | To AI model | Retention | Deletion path |
|---|---|---|---|---|---|---|
| AI call telemetry: request ID, revision ID, stage, deployment, latency, cost, error code | API | Application logs / App Insights | Operators | No (it records no prompts or user text, `ai/stages.py` `Telemetry`) | Log Analytics 30 days (configured in `monitoring.bicep`) | Expiry only |
| Request logs | Container Apps | Log Analytics | Operators | No | 30 days (configured), 1 GB/day cap | Expiry only; redaction filter not built (D3) |
| Database backups | Azure | Postgres backup | Operators | No | 7 days (configured) | Expiry only |
| Blob soft-delete copies | Azure | Storage | Operators | No | 7 days (configured) | Expiry only (F-01) |
| Waitlist and tailor sign-up: name, email, role, optional area, consent tick | Visitor | **Nowhere yet**: the PR #7 form does not send or store | Founders (once connected) | No | Not set: the privacy page says "to be set by the founders" (F-09) | Email request route to be named |
| Outreach tracker (counts, codes `T01`, dates) | Team | Repo CSV template | Team | No | Per protocol | n/a: no names recorded until the research consent form is approved |
| Research media, session notes, consent forms | Participants | Outside app (D7 kit) | Research team | No | Per approved protocol (F-10) | Per protocol |

## 3. What goes to the AI model, in one view

| Stage (PR #10) | Payload | Contains personal data? | Control |
|---|---|---|---|
| A confirm garment | none (local rule) | No | n/a |
| B parse inspiration | `{inspiration_text}` after the safety screen | Possibly: users may type personal details into free text | Screen; prompt says input is data; output must match an enum-only schema. **No filter removes names or emails from the text (gap, F-08)** |
| C load context | none (local) | No | n/a |
| D propose candidates | `{attributes (enums), allowed_recipes}` | No | Allow-list validation |
| E-H | none (engine, local) | No | n/a |
| Future K4 vision assist / stage G image generation | **photos** | Yes | Must update this table, the consent text and the threat model before merge |

Providers receiving data: Azure AI Foundry (model), Azure AI Content Safety (screen, planned). Provider-side retention and region are **unverified** here (F-11).

## 4. Who can see what (operators)

- Anyone with the Azure subscription Owner or Contributor role can read Postgres (via Entra), blobs (via data-plane roles) and logs. Today the shared managed identity is Postgres administrator, Blob Data Contributor and Key Vault Secrets User (K5 modules).
- Developers do not get data-plane access to a pilot database by default. Planned: a documented break-glass procedure (checklist item C-OPS-2).

## 5. Founder decisions required (not chosen here)

| ID | Decision | Why it is open | Current state in the PRs |
|---|---|---|---|
| F-01 | Retention for raw garment photos, and whether blob soft delete (7 days) stays on for `uploads/` | Blueprint §11.4 asks for deletion but gives no period. A "delete" button that leaves a 7-day recoverable copy must be disclosed or removed | Bicep default 30 days since last modification; K5 note "K6 to confirm"; this document does not confirm |
| F-02 | Retention for previews and tailor-brief exports | Derived from photos or measurements | Bicep default 90 days, same note |
| F-03 | Account lifetime, inactivity expiry, and tailor enrolment length | No policy exists | none |
| F-04 | How long to keep the consent record after the data it covers is deleted (audit evidence versus minimisation) | Legal posture | none |
| F-05 | Project, revision and measurement retention while the account is active | Immutable revisions imply keeping history | none |
| F-06 | Body profile retention and whether it is kept after the last project | Highest-sensitivity field | none |
| F-07 | Maker requests, briefs, quotes: retention, and what withdrawal does to a brief a tailor already received | Cannot be recalled technically | none |
| F-08 | Raw inspiration text, job and idempotency records: keep or drop after the job; whether to strip emails and names from the text before the model | Text may hold personal data | not persisted in PR #5 |
| F-09 | Waitlist retention and deletion contact | Site copy says "to be set by the founders" | placeholders in `privacy.html` |
| F-10 | Research participant data and media retention | Pending approved protocol (D7 open item H-05 in `docs/research/`) | none |
| F-11 | Model provider data handling and region | Provider may retain prompts for abuse monitoring; terms must be read from current Microsoft documentation | unverified |
| F-12 | Whether the first pilot allows photos of people at all (face/background handling) | Garment photos often include rooms or people | none |
| F-13 | Applicable law and whether a formal privacy review is needed (blueprint lists "Formal retention and compliance review" as a later item) | Not a legal opinion; K6 cannot supply one | none |

## 6. Gaps summary

1. No deletion, export or withdrawal routes anywhere (contract or API).
2. No users table: nothing to hold role or consent.
3. Local draft is unencrypted and has no purge.
4. EXIF is not stripped.
5. Redaction of logs is a rule, not code.
6. Retention values in infrastructure are defaults awaiting F-01 and F-02.
7. Backups (7 days) and soft delete (7 days) mean "deleted" is not instant everywhere; the privacy notice must say so once periods are decided.
