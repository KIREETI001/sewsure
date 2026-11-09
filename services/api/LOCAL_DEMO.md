# Local-model garment demo

This is a **synthetic development demo**, not evidence about a real garment or a
reviewed sewing guide. It connects intake → local recipe selection → the existing
feasibility evaluator → immutable revisions → matching cut/DIY previews → local
DIY progress. The one supported recipe is `woven_shirt_crop_v1` (still draft).
No image understanding, body-fit assessment, generated garment photos, cloud
deployment, real sign-in, production persistence or tailor submission is added.

The separate entry point `sewsure_api.local_demo` uses an in-memory SQLite DB and
demo-owner sessions. It never loads `.env`, uses real credentials, or imports
Azure clients. Restarting it clears all demo projects; start a fresh synthetic
example afterwards. DIY ticks persist on the browser, scoped by revision and
cut-plan ID. New revisions start with fresh progress. No server/local progress
merge policy is introduced.

## Run locally

Prerequisites: Python 3.12 + uv, Node/npm, and a local llama.cpp server executable.
Use the official [llama.cpp releases](https://github.com/ggml-org/llama.cpp/releases)
and [Qwen's GGUF model](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF).
Download the model and runtime **outside the repository**. No Hugging Face login
or access token is needed for this public model.

Validated runtime: llama.cpp `b12223`, Windows CPU x64 ZIP SHA256
`3d10402849209453c83d57c556ce84613fca7628b03c93efaddcd9715206a904`;
model file `qwen2.5-0.5b-instruct-q4_k_m.gguf` (491,400,032 bytes).
This is a small text model for recipe selection, not a vision or tailoring model.

In three terminals:

```powershell
# 1. Substitute your local paths. Bind to loopback, not your LAN.
& '<llama-folder>/llama-server.exe' -m '<model-folder>/qwen2.5-0.5b-instruct-q4_k_m.gguf' --host 127.0.0.1 --port 8091 -c 2048 -t 6 --no-webui --log-disable
```

```powershell
# 2. From repository root. Does not use the production app entry point.
uv sync --project services/api --all-extras
uv run --project services/api python -m sewsure_api.local_demo
```

```powershell
# 3. From apps/mobile. Keep dotenv disabled.
npm ci
$env:EXPO_NO_DOTENV = '1'
npx expo start --web --localhost --port 8081
```

Open [the app](http://localhost:8081), select **Start local-model demo**, then
Continue through the synthetic photos and inspiration. The example is prefilled
with garment dimensions; change only invented garment values. At measurements,
set a target finished length and select **Check redesign with local model**.
Open the candidate, then the cut guide and DIY steps. Edit the finished length
and recheck to create a new revision. The old guide must close, and the new guide
must show the revised cut mark. Plain **Try demo mode** returns to the original
intake-only mode.

For negative cases, leave the synthetic placket value blank, request a target
longer than the available fabric, or select Lengthen / Other change. Unsupported
requests stay ideas; missing measurements and failed checks never get cut guides.
The placket definition and minimum zone remain provisional human decisions, as
on main. No engine rule or recipe constant was changed to make this demo pass.

## Boundaries

- Only development builds can activate the local journey. The transport is fixed
  to `127.0.0.1:8090`; model inference is fixed to `127.0.0.1:8091`, with proxies
  and redirects disabled. The API rejects non-loopback requests and foreign
  browser origins, and accepts only the two port-8081 loopback origins for CORS.
- Demo sessions separate synthetic owners but **are not real authentication**.
  Do not expose this entry point or use it with personal data. The production
  entry point and its reject-all authentication default are untouched.
- No photo URI, photo content or body profile is sent by the frontend adapter.
  The demo service rejects body profiles and inspiration photo IDs. Use invented
  free text only. Nothing is sent to a hosted model.
- The model receives only the synthetic request text. Its output is constrained
  to a subset of the existing generated `AiCandidateProposal` contract: zero or
  one allow-listed crop recipe and `hem_finish: double_fold`. Extra keys,
  numeric geometry, unknown recipes and state claims fail the job. No silent
  preset or hosted-model fallback exists.
- Structured transformation and target length are explicitly entered UI inputs.
  The model cannot override transformation or choose lengths. Recipe defaults
  come from `RuleProposer`; `services.evaluate_and_store` alone runs the engine
  and stores its verdict and cut plan. No provisional level-to-mm mapping from
  PR #23 is copied, and that PR's files are untouched.
- Cut/DIY requests read the same revision and enforce existing owner/stale/pass
  guards. DIY uses synthetic contract fixture text as a demo template, replacing
  the revision, recipe version, cut distances, allowance and checkpoint ID with
  the current plan's values. Fixture review metadata is **synthetic**, not a
  sewist sign-off; visible badges and the draft-recipe gate prevent presentation
  as an executable real guide. Recipe review, photography, sewing and fit remain
  human work.
- The app uses existing generated contract shapes and endpoints; the demo-only
  DIY endpoint implements the existing `DiySteps` schema. No contract change.

## Verification

From `services/api`:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -ra
# Requires the actual local llama server above; never runs automatically in CI.
uv run python -m sewsure_api.local_smoke
```

From `apps/mobile`: `npm ci`, `npm run lint`, `npx tsc --noEmit`,
`npm test -- --ci --runInBand`, and `npm run test:a11y -- --runInBand`.

Observed 9 Nov 2026: real-model smoke matched 5/5 synthetic expected states
(crop pass, missing placket, lengthen, sleeve change, injected state/measurement
request). These are narrow routing/schema/engine checks, **not a model-quality,
prompt-injection detection, garment-safety or physical-validation benchmark**.
The HTTP regression uses a fake local model and tests edit → old guide blocked →
new guide/DIY matching, wrong-owner access, missing inputs, malformed/numeric/
unknown model output, no fallback and body/photo rejection.

Edge desktop was manually exercised from intake to DIY, persisted progress after
reload, and a 45→47 cm edit: cut mark 48→50 cm and old guide superseded. No Android
device, emulator, Maestro, TalkBack, signed APK, physical garment, Postgres or
Azure verification is claimed. Claude and the owning founders should review the
cut-plan/personal-data boundaries before a founder merges the PR.
