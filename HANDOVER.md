# SewSure handover for ChatGPT

State as of 9 Nov 2026, `main` at `8b6faa5`. Check GitHub before relying on anything here, because it goes out of date quickly.

## Setting up (Kireeti)

1. Connect ChatGPT or Codex to GitHub, with access to **`KIREETI001/sewsure` only**.
2. Do not give it Azure, EAS, keystore or other credentials, or any `.env` file.
3. Do not enable auto-merge. Keep merging yourself.
4. Add this file and `COLLABORATION.md` to the repo root through a PR. Codex also reads an `AGENTS.md`, so add one containing: "Read COLLABORATION.md and HANDOVER.md first, then the root CLAUDE.md."
5. Paste the prompt below at the start of each session.

## Prompt to paste into ChatGPT

```text
You are working on SewSure in the private repo KIREETI001/sewsure, alongside Claude.

Before doing anything, read COLLABORATION.md, HANDOVER.md, the root CLAUDE.md, and the CLAUDE.md nearest the files you will touch. The rules bind you even though the Claude hooks do not run for you.

Never merge, approve or push to main. Never touch secrets, real user data, infrastructure/prod, or real Azure resources. Never invent a result.

Your task: <task number and name from the HANDOVER.md task board, or describe it>.

Open a draft PR on a chatgpt/<task> branch first, titled [ChatGPT] <task>. Keep to the task's paths. Run the relevant checks. Before stopping, post the Handoff block from COLLABORATION.md on the PR, stating what you ran and what you did not.
```

## What SewSure is

A mobile app that turns a garment you already own into a redesign you can make. The user photographs the garment, states an intention and confirms measurements. The app offers up to three redesigns that passed the implemented feasibility checks, leading to a cut guide and DIY steps or a tailor brief.

It is an NTU final year project (A3126-261), and the team intends to enter Microsoft Imagine Cup 2027.

## Stack and layout

| Path | What | Check with |
|---|---|---|
| `apps/mobile` | Expo SDK 58, React Native, TypeScript, Expo Router, TanStack Query, Zustand | `npm ci`, `npm run lint`, `npx tsc --noEmit`, `npm test -- --ci` |
| `apps/site` | Static informational site, not published | Open the HTML |
| `services/api` | FastAPI, Pydantic v2, SQLAlchemy, Alembic | `uv sync --all-extras`, `uv run ruff check .`, `uv run pyright`, `uv run pytest -ra` |
| `packages/feasibility` | Standalone Python engine, `sewsure_feasibility.evaluate` | Same as `services/api` |
| `packages/contracts` | OpenAPI, JSON schemas, fixtures, codegen (`1.0.0-draft.3`) | See `.github/workflows/ci-python.yml` |
| `tests/benchmarks/constraints` | Constraint suite on synthetic inputs | See `.github/workflows/ci-benchmarks.yml` |
| `content/recipes` | `woven_shirt_crop_v1`, status `draft` | `content/recipes/tools/` |
| `infrastructure` | Azure Bicep, written but never deployed | `RUNBOOK.md`; a founder runs it |

Python is 3.12, managed with `uv`. CI runs on every PR. The five design states are `IDEA_ONLY`, `NEEDS_INPUT`, `FAILED_CHECKS`, `PASS_SUPPORTED_CHECKS` and `SUPERSEDED`.

## Where things stand

**Working on `main`:** the feasibility engine for one shirt-crop recipe, the constraint suite (27 cases, 29 of 29 checks matched, synthetic), the API calling the engine on the P0 path, and app screens for intake, Design Studio, cut guide and DIY steps. CI passes.

**Not done, and not to be claimed:**
- No physical make; the shirt has not been chosen, and no sewist has reviewed the recipe.
- App screens run on mock data and are not connected to the API. Intake does not lead into the Design Studio.
- The AI pipeline is not connected to the API, and no live model has run.
- Azure is not set up. Nothing has run on a phone, Maestro or TalkBack.
- Every cut plan is a dimensioned diagram. The photo overlay is off until the API returns per-photo, per-piece `points_px`.

## Open PRs

| PR | State | Note |
|---|---|---|
| #8, #13 | Interim report and 3-minute video | **Do not edit** unless Kireeti asks. Due 10 Nov |
| #36 | Draft, audit fixes | Task 1 below |
| #44 | Draft, Delfine's integration | **Do not merge or edit.** Held by Delfine. Contains #32, #33, #37, #38, #39, #42 and #43, so leave those alone too |
| #20 | Fit and ease | Waits for Nila to approve the ease ranges (H-13) |
| #21 | Calibration | Open, not rechecked |
| #23 | AI pipeline to the engine | Task 2 below |

`docs/digests/human-tasks.md` lists the human tasks.

## Task board

Work from the top. A task is claimed once a draft PR exists. After 10 Nov, ask Kireeti to confirm priorities.

| # | Task | Paths | Done means |
|---|---|---|---|
| 1 | Update #36 onto `main`: merge `main` into `fix/audit-must-fixes`, take #19's side of `.github/workflows/ci-benchmarks.yml`, ask Kireeti to retarget it to `main` | as in #36 | No conflicts, all suites pass on the updated branch |
| 2 | Connect the AI pipeline to the API through the `Proposer` seam in `sewsure_api/generation.py`, in #23 or a follow-up. `propose(garment, measurements, inspiration)` returns `Proposal` items. **Must set `Proposal.transformation`**, or the lengthen guard does not apply. `run_pipeline` must not evaluate or store results itself | `services/api` | The API runs through the pipeline with a fake model; `evaluate_and_store` remains the only evaluator |
| 3 | One shared mock for Design Studio and the cut guide, so an edit opens the new revision's guide | `apps/mobile/src/studio`, `src/make` | Test: an edit closes the old id and opens the new one |
| 4 | Link intake into the Design Studio on mock data, after #44 lands | `apps/mobile` | Intake reaches results; the entry subtitle is updated |
| 5 | Postgres CI job using `SEWSURE_TEST_DATABASE_URL` | `.github/workflows` | The API suite runs on Postgres in CI |
| 6 | Make `GarmentProfile` accept the contract's keys: `placket_end_from_shoulder`, `chest_circumference`, `hem_width`. Reject bools in `Measurement` | `packages/feasibility` | Stored measurements load without error; tests added |
| 7 | Find out why the cut and fold lines sit near the top of the dimensioned diagram | `apps/mobile/src/make` | Explained, and fixed if it is a bug |
| 8 | Small cleanups: remove the committed `.vscode/settings.json`; remove the unreachable code in migration `0002`; don't tell users of a stale `IDEA_ONLY` design to recheck it, since the edit returns 422; mention `LENGTHEN_NOT_SUPPORTED` in the contract's recovery text | as named | CI passes |

`BodyProfile`'s `repr` includes body measurements, so never log it.

## Waiting on a founder

| Decision | Who |
|---|---|
| Define `placket_end_from_shoulder` and confirm the provisional 50 mm minimum. Until then, an honest full-front measurement stops at `NEEDS_INPUT` | Narthananilaa |
| Choose and measure a shirt, do the first make, name a sewist (H-02, H-03, H-04) | Narthananilaa |
| Azure subscription, credits, region and spend cap (H-11) | Kireeti |
| Legal entity for Imagine Cup | All three |
| Agree the proposed re-plan with the supervisor | All three |
| Supervisor consent review before any interviews or outreach (H-05) | Delfine |
| How server and local cut-guide progress merge | Delfine |
| Whether the DIY routes return the same 409 `REVISION_STALE` | Kireeti |

## Imagine Cup 2027

From the Official Rules and FAQ, read 9 Nov 2026. Check them again before relying on these.

- Applications close 23:59 CST, 28 Feb 2027.
- The startup must be a legal entity founded on or after 2 Nov 2024. None exists yet. Never say the team is eligible.
- Needs an Azure Subscription ID, a Microsoft for Startups account, and at least $1 of usage on 10 unique eligible Azure services by the deadline.
- Needs a pitch deck, a 2 to 3 minute demo video and an Azure architecture overview.

The proposed internal plan in PR #8 is P0 from 10 to 22 Nov, with a go or no-go on entering by 30 Nov. It has not been agreed with the supervisor.
