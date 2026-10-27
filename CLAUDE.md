# SewSure

SewSure is a mobile app that turns a garment the user already owns into a redesign they can actually make. The user photographs the garment, states an intention, confirms measurements, and gets up to three redesigns that passed the implemented feasibility checks. A checked design leads to a calibrated cut guide and DIY steps, or to a tailor-ready brief.

Source documents (outside this repo, in the parent folder): Technical Implementation Blueprint V0.1, Product Scope V0.2, Advisor Presentation, FYP deadlines. Section numbers below (§) refer to the blueprint.

## Who owns what

| Area | Human lead / approver | Paths |
|---|---|---|
| Platform, backend, Azure AI, cloud spend, release | Kireeti | `services/`, `infrastructure/`, `.github/workflows/` |
| Garment rules, feasibility, recipes, evidence | Narthananilaa | `packages/feasibility/`, `content/recipes/`, `tests/benchmarks/`, `docs/evaluation/` |
| Mobile app, UX, research, pitch, website | Delfine | `apps/`, `docs/research/`, `docs/pitch/` |
| Shared contract | All three | `packages/contracts/` |

Agents live in `.claude/agents/`. IDs: L0 lead, K1–K8 (Kireeti), N1–N7 (Narthananilaa), D1–D9 (Delfine), X1–X4 (shared).

## Non-negotiables

1. **Millimetres internally.** All stored and computed lengths are integer or decimal mm. Convert to cm only in the UI. Every measurement records its origin and `confirmed_at`.
2. **Design states are set by the feasibility engine only** (`packages/feasibility`): `IDEA_ONLY`, `NEEDS_INPUT`, `FAILED_CHECKS`, `PASS_SUPPORTED_CHECKS`, `SUPERSEDED`. The AI model, the API and the app never set or upgrade a state themselves.
3. **Revisions are immutable.** Any edit creates a new revision ID and invalidates downstream previews, cut plans, DIY steps and briefs until rechecked.
4. **The AI model never invents numeric pattern geometry.** It may only pick recipe IDs and parameters from an allow-list, validated against a JSON schema (§4).
5. **An unverified image can never reach a "safe to cut" screen.** Previews are labelled approximate.
6. **No guarantee language** anywhere in code, UI strings, docs or pitch: no "guaranteed fit", "perfect fit", "precision AR", "100% accurate". Every number in docs or pitch needs a source and a denominator.
7. **No secrets, real user photos or body measurements in the repo, prompts or logs.** Use synthetic or consented fixtures. Model keys live only on the server (Key Vault), never in the app.
8. **Mobile never assumes a candidate exists or that exactly three exist.**
9. **Contract first.** API and record shapes change only in `packages/contracts` with a change note and an updated contract test, reviewed by the consuming owner.

## How agents work here

- Work in a branch, open a pull request, never push to `main`, never merge, never approve.
- Stay inside the paths your agent file lists. If the task needs a change elsewhere, open an issue for the owning agent and say so in your PR.
- Every PR names a user story and includes either a test or evidence (screenshot, API trace, physical record). Follow the PR checklist in §18.1.
- Tasks needing a human (sewing, sending messages, accounts, consent, signing keys, submissions, approvals) get the label `needs-human` and are listed for the lead agent. Prepare drafts; do not perform them.
- Approval levels: A0 auto, A1 owner, A2 owner + consuming owner, A3 all three, H human only.

## Repo layout

```
apps/mobile/          Expo + React Native + TypeScript app
apps/site/            informational website + waitlist
services/api/         FastAPI service, auth, orchestration, AI pipeline
packages/feasibility/ rules, geometry, fit, calibration (standalone Python)
packages/contracts/   OpenAPI, JSON schemas, fixtures, codegen
content/recipes/      reviewed sewing recipes + rights metadata
tests/benchmarks/     constraint, overlay and model regression cases
docs/                 ADRs, research, evaluation, pitch, reports
infrastructure/       Azure Bicep (azd), budgets, deployment
```

## Tooling (planned)

Python 3.12 with `uv`, ruff, pyright, pytest, Hypothesis. Node LTS with Expo, TypeScript, Jest, Maestro. The project hooks in `.claude/hooks/` format files after edits and block edits to secrets, keystores and `infrastructure/prod/`.
