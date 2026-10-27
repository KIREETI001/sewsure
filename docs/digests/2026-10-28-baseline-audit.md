# Baseline audit vs the P0 exit gate — 2026-10-28

L0 Lead Agent, first run. Audited `main` at commit `84efce5` ("Set up SewSure monorepo, agent definitions and guard hooks"), the only commit on `main`, plus open PRs on github.com/KIREETI001/sewsure.

## The gate

> **P0 pass criterion (blueprint §12, p. 13):** At least one actual user-measured woven shirt produces an internally consistent, reviewed dimensioned cut plan that is physically trialled. Failing the gate means keep the app in demonstration mode and do not expand the transformation library.

P0 window: 22 Oct – 1 Nov 2026 (blueprint §12, proposed internal dates). **4 days left** after today.

## What exists on `main`

| Area | What is there | Evidence |
|---|---|---|
| Project rules | Root `CLAUDE.md` and one `CLAUDE.md` per area (`apps/mobile`, `apps/site`, `content/recipes`, `docs`, `infrastructure`, `packages/contracts`, `packages/feasibility`, `services/api`, `tests/benchmarks`) | `main@84efce5` |
| Agents | 29 agent definitions in `.claude/agents/` (L0, K1–K8, N1–N7, D1–D9, X1–X4) | `main@84efce5` |
| Guard hooks | `.claude/hooks/` format-on-edit, guard-outbound, guard-paths, guard-shell; `.claude/settings.json` | `main@84efce5` |
| Code owners | `.github/CODEOWNERS` maps each area to its founder; branch protection on `main` requires 1 approving review and code-owner review | `main@84efce5`; GitHub branch protection API |
| Everything else | Empty folders with `.gitkeep` only: `apps/mobile`, `apps/site`, `content/recipes`, `docs/adr`, `docs/evaluation`, `docs/pitch`, `docs/reports`, `docs/research`, `infrastructure/prod`, `infrastructure/staging`, `packages/contracts`, `packages/feasibility`, `services/api`, `tests/benchmarks` | `main@84efce5` |
| CI | **None.** No `.github/workflows/` | `main@84efce5` |
| Issues | **None** | GitHub issues list, 2026-10-28 |
| Open PRs | 1: [#1 Add backup code owners for each area](https://github.com/KIREETI001/sewsure/pull/1) (review required, no checks) | GitHub PR list, 2026-10-28 |

## P0 exit evidence, item by item (blueprint §12)

| # | Exit evidence (§12) | Owner (§12) | In repo? | Wave-1 agent working on it |
|---|---|---|---|---|
| E1 | Approved JSON/OpenAPI fixture | All | **No.** `packages/contracts/` is empty | K1 Contract Architect |
| E2 | Real structured response, logs, failure handling | Kireeti | **No.** `services/api/` is empty; no Azure smoke-test trace | K2 API Builder, K3 AI Pipeline, K5 Infra |
| E3 | Unit tests and a dimensioned cut plan | Narthananilaa | **No.** `packages/feasibility/` and `tests/benchmarks/` are empty | N1 Geometry Engine, N2 Constraint Tests |
| E4 | Installable build / end-to-end mock path | Delfine | **No.** `apps/mobile/` is empty | D1 Design System, D2 Intake Flow, K5 (EAS) |
| E5 | Photo and measurements of outcome | All, Narthananilaa lead | **Unknown.** Physical work happens off-repo | Humans only (H-02, H-04); N5 drafts the recipe |

Supporting release gates (§18.3):

| Gate | Unblocking evidence (§18.3) | Status |
|---|---|---|
| G0 – API + recipe | Frozen contract and passing unit tests | Not met: no contract, no tests |
| G1 – first physical cut | Human ruler check + signed-off reviewed recipe | Unknown: no recipe in `content/recipes/`, no reviewer named |

Pass-criterion parts:

| Part of the criterion | Status |
|---|---|
| Actual user-measured woven shirt | Unknown (question Q1) |
| Internally consistent cut plan | Not in repo (needs N1 engine + N2 tests) |
| Reviewed | Not in repo; reviewer not named (Q3, H-03) |
| Dimensioned | Not in repo |
| Physically trialled | Unknown (Q4) |

**Gate status: RED.** 0 of 5 exit-evidence items are linked in the repo (E1–E4 absent, E5 unknown), with 4 days of the P0 window left. This is a repo-evidence status: physical work may already exist and would change E5.

## Questions for the founders (physical progress is unknown to L0)

Please answer in reply to the PR or the digest. Answers go into the next digest.

1. **Q1 — Source shirt.** Has a real woven button-up shirt been chosen for the first trial? Whose is it, and what fibre/weave and condition?
2. **Q2 — Measurements.** Has it been hand-measured? Which landmarks, how many repeat readings, and what was the repeat variation in mm? Where is the record kept (it must stay out of the repo unless synthetic or consented)?
3. **Q3 — Reviewer.** Who will review the crop recipe and construction sequence (blueprint §8.2: "an experienced sewist or supervisor")? Have they agreed?
4. **Q4 — Trial.** Has any marking, cutting or sewing happened yet, on the shirt or on scrap fabric? Any measured deviation between planned and actual marks?
5. **Q5 — D01.** Is the first recipe agreed as "woven button-up crop, measure from a standardised landmark, reviewed hem finish"? Which hem finish?
6. **Q6 — Azure.** Is the Azure subscription live with credits, and is a Foundry / Azure OpenAI model deployment reachable? What is the spend cap?
7. **Q7 — Android device.** Which physical Android device will we test on (D10)?
8. **Q8 — If P0 slips past 1 Nov.** Do you accept the blueprint fallback: keep the app in demonstration mode and do not expand the library (§12), protecting the shirt crop first (§19.1 step 1)?
9. **Q9 — Interim report.** Is the FYP interim report (due 10 Nov 2026) one joint report or one per student, and who is the supervisor/examiner to submit to?

## Gaps L0 cannot fix (outside L0's paths)

- **No CI.** Owner K5 (`.github/workflows/`). Without CI, the digest cannot report failing checks and PRs carry no test evidence. Recommend K5 adds a minimal lint/test workflow in wave 1.
- **No `needs-human` label** in the repo, although `CLAUDE.md` requires it. Creating labels is a repo setting change; listed as H-07 for Kireeti.
- **No cost report source.** K7 is queued, so agent and Azure spend vs cap cannot be reported yet.
