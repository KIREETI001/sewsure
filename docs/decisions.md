# Decisions D01–D13

Owner: L0 Lead Agent (maintains the list; never decides). Decisions at A1 and above are made by the named humans.

Source: Technical Implementation Blueprint V0.1, §20 "Open decisions and approval checklist" (p. 20–21). Owner, proposed answer and approval needed are copied from the blueprint. All proposed answers are **proposed**, not agreed.

Last reviewed: 2026-11-01. D01–D13 are all still open: no agreement is recorded in the repo, and merged code does not count as a decision.

## Status key

- **open**: not decided.
- **agreed**: decided by the owner(s), with the approval evidence linked.
- **superseded**: replaced by a later decision; link it.

## Decision list

| ID | Decision | Owner | Proposed answer (§20) | Approval needed (§20) | Status | Blocks | Recorded outcome |
|---|---|---|---|---|---|---|---|
| D01 | First recipe | Narthananilaa | Woven button-up crop, measure from a standardised landmark, reviewed hem finish | Pattern reviewer + team | open | P0 gate, N1, N5, K1 fixture | — |
| D02 | Next creative recipe | All | Controlled waist shaping or sleeveless conversion only after P0 make | Sewist feasibility review | open | N7 (after P0 green) | — |
| D03 | Tee expansion | Narthananilaa | Relaxed jersey crop/cut-off only, conditional | Separate test garment/material evidence | open | N7, P2 | — |
| D04 | Accessory pilot | All | Select zero or one first; postpone if P1 gate late | MVP classification | open | N7, P2 | — |
| D05 | Scoring | Kireeti + Narthananilaa | Hard feasibility before soft rank; draft weights documented | Testing rubric | open | P2 ranking, K3 | — |
| D06 | Avatar | Delfine | Simple 2D silhouette with measurement labels | Design mock-up reviewed | open | D3, D1 | — |
| D07 | AI vision | Kireeti | Model-assisted category and landmark suggestion with manual correction | Access + quality benchmark | open | K4 | — |
| D08 | Azure services | Kireeti | Foundry/Azure OpenAI core; Search/Speech optional, verify competition fit | Credits and rule check | open | K3, K5 | — |
| D09 | Marketplace | Kireeti + Delfine | Requests and quotes; acceptance/contact state simple | No formal booking claim without flow sign-off | open | K8, D5 | — |
| D10 | Android | Delfine | Expo-based Android APK first | Available test device confirmation | open | D2, D6, K5 (EAS) | — |
| D11 | Cost | Kireeti | Alert and per-design budget target after initial measurements | Supervisor funding check | open | K7, K5 budget alerts | — |
| D12 | Research | All | 24 constraint cases, 4 makes, 8–12 users, 2–3 makers as targets | Ethics/consent and supervisor review | open | D7, N2, N6 | — |
| D13 | Dates | All | P0–P4 internal window; 7 Jan is not official deadline | Portal/rules confirmation | open | D8, X3, submission | — |

## Status notes, 1 Nov 2026

Facts from `main@c46c5d8` and GitHub. None of these changes a status.

| ID | Note |
|---|---|
| D01 | Built ahead of the decision: draft recipe (#11), engine (#12) and fixtures (#15) all assume the woven shirt crop. Reviewer not named; recipe `status: draft` |
| D06 | D3 is running, so this answer is now needed |
| D08 | Code targets Azure Foundry (#10) and Bicep is merged (#6), but no deploy or live call has run. Credits and rules unchecked (H-11, H-09) |
| D10 | Expo app is merged (#14). No `eas.json`; test device unconfirmed (H-06) |
| D11 | `main.bicep` has a default `budgetAmount` of 50. This is a parameter, not an agreed cap. Supervisor funding check not recorded |
| D12 | Targets unchanged. The #19 run reports 27 cases and 29 checks, against the proposed target of 24 cases. Consent form is still a draft (#3, H-05) |
| D13 | Not confirmed on the portal (H-09). P0's internal date passed without a pass |

## Process items outside D01–D13

| ID | Item | Owner | Status | Evidence or L0 recommendation |
|---|---|---|---|---|
| P-01 | Approvals on `main` are optional; a PR is still required; any founder can merge | Kireeti | **Recorded** | #16; branch protection API, 1 Nov: 0 required approvals. X2 on #8 still asks for the date and reason, for the report |
| P-02 | P0 re-plan after the missed exit date (§12 requires "a documented re-plan") | All three | **open** | L0 proposes a first make by Wed 4 Nov, keeping demonstration mode and no library expansion until the gate passes |
| P-03 | Whether to close the shared-account merge route, now GitHub requires no review (raised by X2 on #13) | All three | **open** | Agents open PRs from the KIREETI001 account. Hooks block `gh pr merge`, but GitHub itself would not stop a merge from that account. L0 recommends the founders decide before the interim report describes this process |

## L0 recommendations (not decisions)

Sorted by critical-path impact (§13.1).

1. **P-02 and D01 now.** The first make depends on both, along with the named reviewer (H-02).
2. **D08 and D11, then D10.** The first two need H-11; D10 needs a confirmed device. All three feed P0 exit evidence ("real structured response", "installable build").
3. **D12 before any participant session.** Ethics and consent must be approved before D7 schedules users or tailors.
4. **D13 and P-03 before the report and video are final.** Both affect what they can truthfully say.
5. **D06 soon**, since D3 is running. D02, D03, D04, D05, D07 and D09 can wait until after the P0 gate.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-28 | Created from blueprint §20. All 13 open. | L0 |
| 2026-11-01 | Status notes added after 14 merges; all 13 still open. Process items P-01 to P-03 added. | L0 |
