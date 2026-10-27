# SewSure: FYP Interim Report (DRAFT v0.1)

| | |
|---|---|
| Project | SewSure: turning a garment the user already owns into a redesign they can make |
| Students | Kireeti, Narthananilaa, Delfine `[FOUNDER INPUT NEEDED: full names, matric numbers, project code as they appear on the NTU report template]` |
| Supervisor | Dr Wesley `[FOUNDER INPUT NEEDED: full name and title; examiner's name]` |
| Programme | School of EEE, Final Year Project, FYP 2026 S1 (Aug 2026 – May 2027) [S5] |
| Report due | 10 Nov 2026, to supervisor and examiner, with a video presentation [S5] |
| Draft status | Draft v0.1, written 28 Oct 2026 from the repository at `main@84efce5` and open PRs #1 and #2. Not yet cleared by X2 (claims audit) or by the founders. |

> **How to read this draft.** Facts carry a source tag such as [S3 §12]; `SOURCES.md` maps every tag to a document and location. Text marked **planned** has not happened. Text marked **proposed** is a target that has not been agreed as a threshold. `[FOUNDER INPUT NEEDED: …]` marks work that happens off the repository (sewing, measuring, interviews, meetings) and that this draft cannot know. Nothing in this draft is a result unless it says so.

---

## 1. Introduction

### 1.1 Background

People own clothes they do not wear because of fit, outdated style or low confidence, and many lack the pattern-making and sewing skill to alter them [S1 slide 2]. An AI-generated image of a redesign does not show whether the design can be cut from the fabric the garment actually contains [S1 slide 2, slide 7].

SewSure is a mobile app that addresses this. The user photographs a garment, states an intention, confirms garment and body measurements, and receives up to three ranked redesigns that passed the feasibility checks that are implemented. A checked design can lead to a calibrated cut guide and DIY steps, or to a tailor-ready brief [S2 §01; S1 slide 1].

The team ran an exploratory survey (n = 25). It is a small, non-representative sample and gives directional signals only [S1 slide 2; S2 §01]:

| Finding | Count (denominator 25) |
|---|---|
| No sewing experience or beginner | 24 |
| Had rejected second-hand clothing because of fit | 17 |
| Rated the proposed tool 4 or 5 for usefulness | 21 |
| Would consider finding a tailor through the app in the stated scenario | 12 |

These findings do not show willingness to pay or technical accuracy [S2 §01]. `[FOUNDER INPUT NEEDED: survey date, how respondents were recruited, and the questionnaire, so the method can be stated.]`

The team's own preliminary observation is that existing tools (Stitch Switch, ReStitch, SewPal, local tailors) each cover part of the path from inspiration to execution. This is unverified [S1 slide 3] and is not used as a claim here.

### 1.2 Purpose

The project asks whether generative AI can propose garment redesigns while a deterministic engine, not the AI, decides whether a design passes checks that are physically meaningful. The core technical idea is "generative AI proposes, deterministic calculation checks" [S1 slide 7]. The AI model may only choose recipe IDs and parameters from an allow-list and may never invent numeric pattern geometry [S6 `CLAUDE.md`, rule 4; S3 §4.1].

### 1.3 Scope

Garment coverage is deliberately narrow [S2 §03; S1 slide 4]:

| Level | Garments | What SewSure may claim |
|---|---|---|
| 1, verified flagship | Oversized woven button-up shirts | Redesign, fit checks and calibrated cutting plans, for validated transformations only |
| 2, verified limited | Oversized cotton jersey tees | A smaller library with conservative stretch handling. **Conditional** |
| 3, inspiration only | Other garments | Concept ideas labelled unverified; no cutting map, no "feasible" badge |
| Accessory pilot | 1–2 recipes (for example headband or tote) | **Proposed, conditional**: verified only if material area and seam rules are tested |

Core features: garment intake, AI design studio, checked options, controlled customisation, calibrated static cut overlay with a dimensioned-diagram fallback, DIY steps with manual checkpoints, and an in-app tailor request and quote flow with no payments [S2 §05, §08, §09, §11]. Live camera AR, photo try-on, progress-photo feedback and 3D drape are stretch or future [S2 §07, §08].

**Non-claims.** A design passes only the checks actually implemented. SewSure does not promise perfect fit or construction success, and a line on a phone screen is not necessarily centimetre-accurate on fabric [S2 §03, §08].

### 1.4 Objectives

Objectives come from the Technical Blueprint V0.1 [S3 §1.1, §2, §17]. They are proposals that the three students and the supervisor still need to approve [S3 cover page].

1. **O1.** One real, user-measured woven button-up shirt yields an internally consistent, reviewed, dimensioned cut plan that is then physically trialled (the P0 gate) [S3 §12].
2. **O2.** A connected mobile prototype carries a photo through measurement confirmation, AI interpretation and checked options to a 2D preview and a DIY sequence [S3 §12, P1; S1 slide 14].
3. **O3.** Design states (`IDEA_ONLY`, `NEEDS_INPUT`, `FAILED_CHECKS`, `PASS_SUPPORTED_CHECKS`, `SUPERSEDED`) are set only by the feasibility engine, revisions are immutable, and an unverified image can never reach a "safe to cut" screen [S6 `CLAUDE.md`, rules 2, 3, 5; S3 §1.1].
4. **O4.** Evaluate with evidence that keeps failures: a **proposed** 24-case constraint suite, **proposed** 4 physical makes, **proposed** 8–12 design participants and 2–3 makers [S1 slide 12; S3 §17.2, §20 D12]. V0.2 has not agreed numeric thresholds [S1 slide 12; S2 §12].

### 1.5 Project plan and timeline

Dates below are internal planning windows proposed on 22 Oct 2026. They are not confirmed external deadlines, and scope advances only after each phase's exit gate [S3 §12].

| Phase (proposed) | Window | Purpose | Exit evidence (proposed) |
|---|---|---|---|
| P0 | 22 Oct – 1 Nov 2026 | Prove one measurable transformation | Fixture, live structured response, unit tests and a dimensioned cut plan, installable build, photo and measurements of a physical outcome [S3 §12] |
| P1 | 2 – 15 Nov 2026 | Connected alpha | Three-case trace, pass/fail suite, APK video on a device, sign-off checklist [S3 §12] |
| P2 | 16 Nov – 6 Dec 2026 | MVP integration | Up to three distinct checked results, overlay error report, one user-to-tailor test request [S3 §12] |
| P3 | 7 – 15 Dec 2026 | Validation and stabilisation | Benchmark with denominators, four physical makes, de-identified task metrics, frozen build [S3 §12] |
| P4 | 16 Dec 2026 – 7 Jan 2027 | Evidence, demo, submission preparation | Reproducible analysis, rehearsed demo, release runbook [S3 §12] |

The advisor deck puts the dependency gate plainly: do not widen garment coverage until the first measured transformation passes validation and a physical make confirms planned against actual dimensions [S1 slide 13].

NTU milestones for FYP 2026 S1 [S5]:

| Milestone | Date |
|---|---|
| Project plan / strategy to supervisor | 14 Sep 2026 `[FOUNDER INPUT NEEDED: was this submitted, and where is the copy?]` |
| **Interim report and video presentation** to supervisor and examiner | **10 Nov 2026** |
| Draft final report to supervisor | 25 Mar 2027 (read from the NTU table; confirm) |
| Final report to supervisor and examiner | 9 Apr 2027 (read from the NTU table; confirm) |
| Project demonstration (arranged with examiner) | Week of 12 – 16 Apr 2027 (read from the NTU table; confirm) |
| Oral presentation | 10 – 12 May 2027 window; date and venue to be announced by NTU (confirm) |
| Revised final report and library full text | 19 May 2027 (confirm) |

The Imagine Cup 2027 requirements and deadline are unverified [S1 slide 11, slide 13; S3 §12 note]. The 7 Jan 2027 date is an internal target, not an official deadline [S3 §20 D13].

### 1.6 Purpose of this report

This report documents what has been achieved so far and what remains, in the NTU suggested interim format [S4]. It is also an honest status record: at the date of writing, the project is at the start of its build phase, and much of the evidence the plan depends on does not yet exist (see Section 4).

---

## 2. Work done so far

### 2.1 Summary

| Date | Work | Evidence |
|---|---|---|
| Before 21 Oct 2026 | Product Scope V0.1 and earlier feature discussions | [S2 §15] `[FOUNDER INPUT NEEDED: dates and the V0.1 document]` |
| Before 22 Oct 2026 | Exploratory survey, n = 25 | [S1 slide 2] `[FOUNDER INPUT NEEDED: date and method]` |
| 21 Oct 2026 | FYP team meeting; two independent sets of minutes | [S2 §15] |
| 22 Oct 2026 | Product Scope V0.2 reconciled the meeting notes with the owner's clarifications | [S2 cover] |
| 22 Oct 2026 | 14-slide advisor presentation prepared for Dr Wesley, labelled "proposed plan, not results" | [S1 slide 1] |
| 22 Oct 2026 | Technical Implementation Blueprint and three-person plan V0.1 | [S3 cover] |
| 28 Oct 2026 | Monorepo, 29 agent definitions, per-area rules, guard hooks and code-owner file on `main` (one commit) | [S6] |
| 28 Oct 2026 | Branch protection on `main`: pull request, one approving code-owner review | [S8, audit] |
| 28 Oct 2026 | PR #1 (backup code owners) and PR #2 (baseline P0 audit, digest, risk register, decision log) open for review | [S7, S8] |

`[FOUNDER INPUT NEEDED: supervisor meetings held to date, with dates, and what the supervisor advised.]`

### 2.2 Problem definition and scope reconciliation

The scope was reconciled across three inputs: SewSure V0.1, two sets of notes from the 21 Oct meeting, and the owner's 22 Oct clarifications. Where sources conflicted, the owner's clarifications took precedence, then the consistent 21 Oct decisions, then V0.1; disputed details were recorded as open [S2 §02].

Changes from V0.1 are listed in Section 3.3. The decision register D01–D12 in the scope document remains largely unresolved [S2 §14], and the blueprint adds D13 on competition dates [S3 §20].

### 2.3 Technical design

The blueprint defines the system and its checks. These are **designs, not implemented features** [S3 cover]:

- **Architecture.** Android-first Expo mobile client; a backend API that owns images, profiles, generation requests, geometry checks and design records; Azure AI services for vision and design proposals; and a custom deterministic feasibility engine with geometry, ease, material and construction rules [S1 slide 11; S3 §2]. Azure service choices are provisional [S1 slide 11].
- **Design record.** A versioned record used by preview, cut plan, instructions and tailor brief. An approved revision is immutable; edits create a new revision that is rechecked before downstream use [S3 §1.1, §3].
- **AI boundary.** The model may select recipe IDs and parameters from an allow-list, validated against a JSON schema; hard failures cannot be out-scored by style ranking [S3 §4.1, §4.3; S1 slide 7].
- **Hard gates and failure codes** for geometry, material, fit and construction, with unit tests written before the app UI [S3 §5.4, §5.5].
- **Cut guidance.** Calibrated static overlay with a dimensioned-diagram fallback, and a rule that a line on a screen is not proof of a centimetre on fabric [S3 §6; S2 §08].
- **Worked example.** A cut-line calculation is shown in the deck for illustration only (a 76 cm shirt cropped to 54 cm with hem allowance). **These are illustrative numbers, not measured results** [S1 slide 8; S3 §5.3].

### 2.4 Engineering method: human-governed, agent-assisted delivery

A three-person team has to cover backend, AI, geometry, mobile, research and reporting inside a few weeks. The team therefore uses AI coding agents (Claude Code) under explicit human control. This is part of the method and is declared in Appendix A.

**Roles.** Each human lead owns an area and approves changes to it [S6 `CLAUDE.md`]:

| Lead | Area | Paths |
|---|---|---|
| Kireeti | Platform, backend, Azure AI, cloud spend, release | `services/`, `infrastructure/`, `.github/workflows/` |
| Narthananilaa | Garment rules, feasibility, recipes, evidence | `packages/feasibility/`, `content/recipes/`, `tests/benchmarks/`, `docs/evaluation/` |
| Delfine | Mobile app, UX, research, pitch, website | `apps/`, `docs/research/`, `docs/pitch/` |
| All three | Shared API and record contract | `packages/contracts/` |

**Agents.** 29 agent definitions are on `main`: one lead (L0), eight for Kireeti's area (K1–K8), seven for Narthananilaa's (N1–N7), nine for Delfine's (D1–D9) and four shared reviewers, writers and testers (X1–X4) [S6 `.claude/agents/`; S6 `CLAUDE.md`]. Each agent file lists the paths that agent may edit. For example, the report writer may edit only `docs/reports/` and `docs/adr/` [S6 `x3-report-writer.md`].

**Process rules** [S6 `CLAUDE.md`, "How agents work here"]:

1. Agents work on a branch and open a pull request. They never push to `main`, merge or approve.
2. `main` requires a pull request with one approving review from a code owner, including for admins [S8 audit; S7 body]. `.github/CODEOWNERS` maps each area to its lead, and PR #1 adds a backup owner per area because a lead cannot approve a PR opened under their own account [S7].
3. Every PR names a user story and carries a test or evidence, following the PR checklist in blueprint §18.1 [S6 `CLAUDE.md`; S3 §18.1].
4. Work only a human can do (sewing, sending messages, accounts, consent, signing keys, submissions, approvals) is labelled `needs-human` and is not performed by agents [S6 `CLAUDE.md`].
5. Approval levels A0 (auto) to A3 (all three founders) and H (human only) set who signs off [S6 `CLAUDE.md`].

**Guardrails in code.** Four hooks in `.claude/hooks/` run on agent tool calls [S6 hooks]:

| Hook | Effect |
|---|---|
| `guard-paths` | Blocks edits to secret and signing files (for example `.env`, keystores, `google-services.json`) and to `infrastructure/prod/` |
| `guard-shell` | Blocks pushing to `main`, force pushes, merging or approving a PR, real Azure provisioning, and store-credential commands |
| `guard-outbound` | Blocks outbound messaging and publishing tools; agents save drafts and a founder sends them |
| `format-on-edit` | Formats edited files when a formatter is installed |

**Non-negotiable rules** that agents and humans both follow include millimetres internally, no invented numeric geometry by the model, no secrets or real photos or body measurements in the repo, no guarantee language ("perfect fit", "precision AR", "100% accurate"), and contract-first changes to API shapes [S6 `CLAUDE.md`].

**Limits of this method, stated honestly.** These controls are written down and the hooks exist, but no CI workflow is on `main` yet, so automated test enforcement is not in place [S8 audit]. The `needs-human` label does not yet exist in the repository [S8 audit]. Agent output is a draft until a human reviews it; agents were not shown to be correct merely by being run.

### 2.5 Wave 1 of agent work

On 28 Oct 2026 the lead agent (L0) reported 14 agents running in parallel, each in its own worktree and branch, with 15 more queued [S8, daily digest]. As of this draft, `main` holds one commit, and the only open PRs are #1 and #2 [S6; S7; S8]. `[UPDATE BEFORE SUBMISSION: list the wave-1 PRs that have been reviewed and merged by then, with PR numbers and merge dates, and what each contains.]`

### 2.6 Physical and user work

The plan depends on physical makes and user sessions, which happen off the repository. L0 could not see any of it, and its audit lists the question for each item [S8 audit, Q1–Q4].

| Item | Status in this draft |
|---|---|
| Source shirt chosen (garment, fibre, condition) | `[FOUNDER INPUT NEEDED: chosen? whose? fibre/weave, condition]` |
| Hand measurements (landmarks, repeat readings, variation in mm) | `[FOUNDER INPUT NEEDED: done? landmarks, number of repeats, variation in mm]` |
| First marking, cutting or sewing on shirt or scrap | `[FOUNDER INPUT NEEDED: any trial? planned vs actual deviation in mm]` |
| Sewist or supervisor reviewer for the recipe (blueprint §8.2) | `[FOUNDER INPUT NEEDED: named? agreed?]` |
| Interviews, usability sessions, maker conversations | `[FOUNDER INPUT NEEDED: number held, dates, participant codes only (P01, T01), consent recorded?]` |
| Azure subscription, credits, model deployment, spend cap | `[FOUNDER INPUT NEEDED: live? reachable? cap?]` |
| Physical Android test device and EAS account | `[FOUNDER INPUT NEEDED: device model, account]` |

No measurement, make or participant data is reported in this draft because none is in the repository. When added, each value needs its denominator and its source record, and negative results must be kept [S9 `docs/CLAUDE.md`].

### 2.7 Effort

- Planning documents: scope V0.2 (10 pages), blueprint V0.1 (21 pages), and a 14-slide advisor deck, all dated 22 Oct 2026 [S1; S2; S3].
- Repository setup and agent governance on 28 Oct 2026: one commit establishing the monorepo, 29 agent definitions, per-area rules, four hooks and a code-owners file [S6].
- `[FOUNDER INPUT NEEDED: hours per person to date, meetings, shopping and material costs, and any time spent that left no document.]`

### 2.8 Problems encountered

| Problem | Evidence | Effect |
|---|---|---|
| **P0 gate is red.** 0 of 5 exit-evidence items were found in the repository: no contract, no API, no feasibility code or tests, no app. The fifth (physical outcome) is unknown to the repo | [S8 audit] | 4 days remained in the proposed P0 window on 28 Oct |
| Scope was still being reconciled on 21–22 Oct; decisions D01–D13 are all open | [S2 §14; S3 §20; S8 `docs/decisions.md`] | Features such as the first recipe cannot be built until D01 is agreed at A3 |
| No CI workflow; no `needs-human` label; no issues | [S8 audit] | PRs carry no automated checks yet |
| Code-owner reviews blocked for single-owner areas; two collaborators had to accept invites before GitHub could request their review | [S7 body] | PR #1 proposes backup owners |
| Imagine Cup 2027 rules and deadline are unverified; the cited competition date is tentative | [S1 slide 13; S3 §12 note] | The internal 7 Jan 2027 date may not match the competition |
| Ethics, consent and deletion route for user sessions is not yet confirmed with the supervisor | [S8 `human-tasks.md`, H-08; S3 §20 D12] | Participant recruitment cannot start until it is |
| `[FOUNDER INPUT NEEDED: other obstacles such as time clashes with other modules, access to materials, tool or budget limits.]` | | |

---

## 3. Future work

### 3.1 In progress

As at 28 Oct 2026, wave 1 of agent work is in progress across the platform, geometry, mobile and documentation areas. Each agent's output reaches `main` only through a reviewed PR [S8 digest; S6 `CLAUDE.md`]. The in-flight items map to the P0 exit evidence [S8 audit]:

| P0 exit evidence | Area in progress |
|---|---|
| Approved JSON/OpenAPI fixture | Contract definition in `packages/contracts/` |
| Real structured response, logs, failure handling | API, AI pipeline and infrastructure in `services/` and `infrastructure/` |
| Unit tests and a dimensioned cut plan | Geometry engine and constraint tests in `packages/feasibility/` and `tests/benchmarks/` |
| Installable build / end-to-end mock path | Design system and intake flow in `apps/mobile/`, EAS build wiring |
| Photo and measurements of the outcome | Human work only; a recipe draft is in preparation |

`[UPDATE BEFORE SUBMISSION: replace this table with the actual state of each item as of 9 Nov 2026.]`

### 3.2 To do (planned)

The following are **planned**, not done. Order follows the blueprint's critical path: garment data contract, real measurements, pattern rule correctness, backend check API, app confirmation, accurate cut guide, physical make, evaluated evidence [S3 §13.1].

1. **Finish P0 (planned, by 1 Nov 2026):** agree the first recipe (D01), measure a real shirt, mark and trial a cut, record the deviation in mm, and complete the five exit-evidence items [S3 §12; S8 `human-tasks.md`, H-01 to H-04].
2. **P1 connected alpha (planned, 2–15 Nov):** structured candidate parser, a three-case trace, one controlled fit adjustment, an APK demonstration on a real device, auth and versioned revisions [S3 §12].
3. **P2 MVP integration (planned, 16 Nov – 6 Dec):** up to three distinct checked results, immutable recheck on edit, calibration and the measured overlay error report, saved body profile, a user-to-tailor test request [S3 §12].
4. **P3 validation (planned, 7–15 Dec):** run the 24 constraint cases including false-pass cases, four physical makes, 8–12 participant sessions and 2–3 maker sessions if consent and recruitment allow, then freeze the build [S3 §12, §17.2].
5. **P4 evidence and submission (planned, 16 Dec – 7 Jan):** analysis with confidence caveats, recorded and rehearsed demo, release runbook, and verification of Imagine Cup rules before any submission [S3 §12].
6. **Final-year deliverables (planned):** draft final report, final report, demonstration and oral presentation on the NTU dates in Section 1.5 [S5].
7. **Gates before claims.** No presentation claim goes out without source, denominator, method and recorded outcome [S3 §18.3, gate G4].

If a milestone slips, the fallback order is: protect the shirt crop with a physical make and an accurate measured cut plan; then mobile intake, measurement correction, design revision and the basic DIY path; then at least one independently useful AI task; then simplify avatars, candidate count and overlay; then reduce the marketplace; and finally postpone tee expansion, accessories, search, speech, AR, try-on and photo checking [S3 §19.1].

### 3.3 Changes to the original requirements

| Topic | Before (V0.1) | Now (V0.2) | Source |
|---|---|---|---|
| Platform | Responsive web app | Mobile app plus a simple informational website | [S2 §13] |
| Pillar emphasis | Three roughly equal pillars | AI Design Studio and DIY primary; tailor path secondary | [S2 §13] |
| Garment breadth | Button-up and tee only | Verified garments, broad inspiration ideas, and a proposed accessory sub-library | [S2 §13] |
| Tailor workflow | Profiles, quotes and booking confirmation | In-app request and quote; booking process undecided; no payments | [S2 §13] |
| Avatar | Measurement-based 2D preview | 2D confirmed; body presets optional; 3D later | [S2 §13] |
| Optional materials | Not scoped | Opt-in additional materials discussed; details open | [S2 §13] |

Further change is expected if the P0 gate stays red: the blueprint says to keep the app in demonstration mode and not expand the transformation library [S3 §12]. Jersey tee, accessory and tailor work are conditional on the primary gate staying green [S3 §12 P2].

### 3.4 Risks to the plan

The blueprint's risk register rates pattern validity and three-person overload as critical, and photo calibration, jersey stretch, AI image mismatch, service access and cost, instruction safety, privacy and the submission schedule as high [S3 §19]. L0 has copied these into a risk register in PR #2 [S8 `docs/risk-register.md`].

### 3.5 Needs-human items

Work agents may only prepare, and that is listed for L0 [S8 `human-tasks.md`]. Items relevant to this report: H-10 (review this draft, record the video, complete the NTU GAI declaration form, submit by 10 Nov 2026), H-08 (supervisor ethics and consent route), and the `[FOUNDER INPUT NEEDED]` items above.

---

## 4. Conclusion

**Honest assessment, 28 Oct 2026.** The project has a clear, narrow scope, a documented design and a working governance model, but little built and no physical evidence yet.

- **Done:** scope V0.2, the technical blueprint, an advisor deck, a small directional survey, and a repository with agent roles, hooks and review rules on `main` [S1; S2; S3; S6].
- **Not done:** no contract, API, feasibility code, tests or app is on `main`, and the repository contains no physical-make record [S8 audit]. The P0 gate was rated **red** on 28 Oct, with four days left in its proposed window [S8 audit]. Physical work may exist off the repository and would change the fifth item; this draft cannot say `[FOUNDER INPUT NEEDED]`.
- **Not claimed:** no feasibility accuracy, rejection rate, overlay error, usability result or cost figure exists. The survey figures are directional only, and the worked example in the deck is illustrative [S1 slides 2, 8].
- **What the next two weeks decide.** If P0 closes (one measured shirt, a reviewed dimensioned cut plan, and a physical trial with deviation recorded), the plan can proceed to a connected alpha. If not, the blueprint's own rule applies: stay in demonstration mode, narrow to the one proven recipe, and re-plan, and this report should say so plainly [S3 §12, §19.1].
- **Schedule.** The remaining plan compresses build, user sessions and four physical makes into 22 Oct – 7 Jan 2027, which is tight, with Dec as the main evidence window [S3 §12]. The NTU final report is not due until April–May 2027 [S5], so the NTU schedule has slack that the internal competition-oriented schedule does not. `[FOUNDER INPUT NEEDED: confirm which schedule governs, and agree with the supervisor.]`
- **Method value and risk.** Agent assistance has allowed the repository and documentation to be set up quickly and with enforceable review rules. Speed on documents is not the same as validated engineering: every geometry rule, recipe and claim still needs human review and a physical test before it counts as evidence [S6 `CLAUDE.md`; S3 §8.2].

`[UPDATE BEFORE SUBMISSION: revise this assessment on 9 Nov 2026 against the real P0 result.]`

---

## References

Internal documents are listed in `SOURCES.md` under tags S1–S9. External references quoted from those documents:

1. School of Electrical and Electronic Engineering, NTU. *Final Year Project* (EEE intranet page, submission deadlines table), printed 22 Oct 2026.
2. School of Electrical and Electronic Engineering, NTU. *Suggested Format of FYP Interim Report.*
3. Microsoft Learn. *Structured outputs, Microsoft Foundry.* https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs (cited in [S3] as M1; not independently checked for this draft).
4. Microsoft Learn. *Event-driven jobs, Azure Container Apps.* https://learn.microsoft.com/en-us/azure/container-apps/tutorial-event-driven-jobs (cited in [S3] as M3; not independently checked).
5. Microsoft Learn. *Storage security guide.* https://learn.microsoft.com/azure/storage/common/storage-security-guide (cited in [S3] as M5; not independently checked).
6. Expo. *ImagePicker.* https://docs.expo.dev/versions/latest/sdk/imagepicker/ (cited in [S3] as E1; not independently checked).
7. Imagine Cup 2027 competition pages (cited in [S3] as C1–C3; dates tentative and unverified).

`[FOUNDER INPUT NEEDED: add any academic references the supervisor expects (garment pattern-making, ease and fit, human-AI decision support) and format them in the NTU style.]`

---

## Appendix A. Declaration of generative AI assistance (notes for the NTU GAI declaration form)

This appendix gives the facts needed to complete NTU's GAI declaration form. **The form itself is completed and submitted by each student** [S5]; this draft does not replace it.

| Item | Detail |
|---|---|
| Tool | Claude Code (Anthropic) running as software agents inside this repository. The exact model version per task is recorded in the PR or commit trailer `Co-Authored-By` |
| Used for in the project | Writing code, tests, documentation and drafts under the agent roles in Section 2.4. All work enters `main` only through a PR with human code-owner approval |
| Used for in this report | Drafting structure and text from the source documents and repository (agent X3, Report Writer). Every factual sentence is tagged to a source in `SOURCES.md` |
| Human input | The source PDFs (scope, blueprint, advisor deck) were produced by the team. Founders supply the physical and user-research facts marked `[FOUNDER INPUT NEEDED]` and review the draft |
| Not delegated | Sewing and measuring, participant contact, consent, accounts, credentials, submissions and approvals are human-only [S6 `CLAUDE.md`] |
| Data given to the tools | Synthetic or consented data only. No secrets, real user photos or body measurements go into the repository, prompts or logs [S6 `CLAUDE.md`, rule 7] |
| Verification | Draft to be checked by the claims auditor agent (X2), then reviewed line by line by each student before submission `[FOUNDER INPUT NEEDED: confirm who reviewed and when]` |
| Limitation | AI-written text can contain errors or unsupported statements. Anything not traceable in `SOURCES.md` should be removed |

## Appendix B. Open placeholders for founders (collected)

1. Names, matric numbers, supervisor and examiner names.
2. Survey date, recruitment method, questionnaire.
3. Dates and notes of supervisor meetings; whether the 14 Sep 2026 project plan was submitted.
4. P0 physical facts: shirt, measurements, trial, reviewer (Section 2.6).
5. Interviews and usability sessions held, with participant codes.
6. Azure, device and account status.
7. Hours of effort and costs.
8. Other obstacles (Section 2.8).
9. Confirmation of NTU dates marked "confirm" in Section 1.5.
10. Which schedule governs (NTU vs internal competition) and academic references.
11. Final status of wave-1 PRs and the P0 result, to replace the `[UPDATE BEFORE SUBMISSION]` markers on 9 Nov 2026.
