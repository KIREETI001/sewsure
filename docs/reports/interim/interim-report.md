# SewSure: FYP Interim Report (DRAFT v0.1)

| | |
|---|---|
| Project | SewSure: turning a garment the user already owns into a redesign they can make |
| Students | Kireeti, Narthananilaa, Delfine `[FOUNDER INPUT NEEDED: full names, matric numbers, project code as they appear on the NTU report template]` |
| Supervisor | Dr Wesley (the advisor deck is addressed to Dr Wesley [S1 slide 1]; `[FOUNDER INPUT NEEDED: confirm Dr Wesley's role, full name and title, and the examiner's name]`) |
| Programme | School of EEE, Final Year Project, FYP 2026 S1 (Aug 2026 – May 2027) [S5] |
| Report due | 10 Nov 2026, to supervisor and examiner, with a video presentation [S5] |
| Draft status | Draft v0.2, revised 1 Nov 2026 after the X1 and X2 reviews of v0.1. Repository facts are as of 1 Nov 2026 (`main@c46c5d8` plus PRs open that day). Not yet cleared by X2 on this revision or by the founders. |
| Status date | **As of `[AS-OF DATE: one date shared with the video script (PR #13); founders to set]`**. Every status statement in Sections 2–4 must be re-checked against this date. |

> **How to read this draft.** Facts carry a source tag such as [S3 §12]; `SOURCES.md` maps the tags to a document and location. Factual claims are tagged; judgments in the Conclusion are the drafter's. Text marked **planned** has not happened. Text marked **proposed** is a target that has not been agreed as a threshold. `[FOUNDER INPUT NEEDED: …]` marks work that happens off the repository (sewing, measuring, interviews, meetings) and that this draft cannot know. Nothing in this draft is a result unless it says so.

---

## 1. Introduction

### 1.1 Background

The team's problem statement is that people own clothes they do not wear because of fit, outdated style or low confidence, and lack the pattern-making and sewing skill to alter them [S1 slide 2]. The only measured figure behind this is the survey below (24 of 25 had no or beginner sewing experience; n = 25, directional). An AI-generated image of a redesign does not show whether the design can be cut from the fabric the garment actually contains [S1 slide 2, slide 7].

SewSure is a planned mobile app intended to address this. The user would photograph a garment, state an intention, confirm garment and body measurements, and receive up to three ranked redesigns that passed the feasibility checks that are implemented. A checked design could lead to a calibrated cut guide and DIY steps, or to a tailor-ready brief [S2 §01; S1 slide 1].

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

Garment coverage is deliberately narrow [S2 §03; S1 slide 4]. These are target support levels. **No transformation has been validated yet.**

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
| P3 | 7 – 15 Dec 2026 (blueprint) | Validation and stabilisation | Benchmark with denominators, four physical makes, de-identified task metrics, frozen build [S3 §12] |
| P4 | 16 Dec 2026 – 7 Jan 2027 (blueprint) | Evidence, demo, submission preparation | Reproducible analysis, rehearsed demo, release runbook [S3 §12] |

P3 and P4 dates follow blueprint §12. Advisor deck slide 13 shows P3 as 7 – 22 Dec and P4 as 23 Dec – 7 Jan, so the two documents disagree [S1 slide 13; S3 §12]; `[FOUNDER INPUT NEEDED: choose one set]`. The proposed P0 window (22 Oct – 1 Nov 2026) has ended [S3 §12].

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
| 28 Oct 2026 | Branch protection on `main` requiring a PR and one approving code-owner review (state on 28 Oct) | [S8 audit] |
| By 1 Nov 2026 | Approval requirement removed from `main` (one required review was seen on 28 Oct): a PR is still required, including for admins, but GitHub requires 0 approving reviews. Review levels A0–A3 became team guidance (PR #16). `[FOUNDER INPUT NEEDED: who changed it, when, and why]` | [S11; S12] |
| 1 Nov 2026 | 14 PRs merged between 18:16 and 18:18 SGT, all from the KIREETI001 account with no approving review. They add a contract draft, a feasibility engine and draft recipe, a constraint suite, an API scaffold, an AI pipeline skeleton, staging infrastructure and CI, an Expo scaffold with intake screens on fixtures, design tokens, a research kit, site and outreach drafts, and L0's baseline audit | [S10; S13] |
| 1 Nov 2026 (snapshot) | 13 PRs open, including this report (#8) and the video script (#13); 15 by 2 Nov after #33 and #34 opened. Re-read at the status date | [S13] |

`[FOUNDER INPUT NEEDED: supervisor meetings held to date, with dates, and what the supervisor advised.]`

### 2.2 Problem definition and scope reconciliation

The scope was reconciled across three inputs: SewSure V0.1, two sets of notes from the 21 Oct meeting, and the owner's 22 Oct clarifications. Where sources conflicted, the owner's clarifications took precedence, then the consistent 21 Oct decisions, then V0.1; disputed details were recorded as open [S2 §02].

Changes from V0.1 are listed in Section 3.3. The decision register D01–D12 in the scope document remains largely unresolved [S2 §14], and the blueprint adds D13 on competition dates [S3 §20].

### 2.3 Technical design

The blueprint defines the system and its checks. These are **designs** [S3 cover]; draft code for some of them (contract, feasibility engine, API and AI skeletons) merged on 1 Nov (Section 2.5), and none of it is validated:

- **Architecture.** Android-first Expo mobile client; a backend API that owns images, profiles, generation requests, geometry checks and design records; Azure AI services for vision and design proposals; and a custom deterministic feasibility engine with geometry, ease, material and construction rules [S1 slide 11; S3 §2]. Azure service choices are provisional [S1 slide 11].
- **Design record.** A versioned record used by preview, cut plan, instructions and tailor brief. An approved revision is immutable; edits create a new revision that is rechecked before downstream use [S3 §1.1, §3].
- **AI boundary.** The model may select recipe IDs and parameters from an allow-list, validated against a JSON schema; hard failures cannot be out-scored by style ranking [S3 §4.1, §4.3; S1 slide 7].
- **Hard gates and failure codes** for geometry, material, fit and construction, with unit tests written before the app UI [S3 §5.4, §5.5].
- **Cut guidance.** Calibrated static overlay with a dimensioned-diagram fallback, and a rule that a line on a screen is not proof of a centimetre on fabric [S3 §6; S2 §08].
- **Worked example.** A cut-line calculation is shown in the deck for illustration only (a 76 cm shirt, 52 cm finished length, 2 cm hem allowance, cut mark at 54 cm). **Illustrative numbers, not measured results** [S1 slide 8]. The blueprint's own example uses different numbers [S3 §5.3]; this report and the video script use the deck's.

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
2. `main` requires a pull request, including for admins. On 28 Oct it also required one approving code-owner review [S8 audit]; as of 1 Nov GitHub requires no approving review, and any founder can merge any PR [S11; S12]. `.github/CODEOWNERS` maps each area to its lead, with backup owners added in PR #1 [S7].
3. Every PR names a user story and carries a test or evidence, following the PR checklist in blueprint §18.1 [S6 `CLAUDE.md`; S3 §18.1].
4. Work only a human can do (sewing, sending messages, accounts, consent, signing keys, submissions, approvals) is labelled `needs-human` and is not performed by agents [S6 `CLAUDE.md`].
5. Review levels A0 (auto) to A3 (all three founders) and H (human only) are team guidance, not enforced by GitHub [S11].

**Guardrails in code.** Four hooks in `.claude/hooks/` run on agent tool calls [S6 hooks]:

| Hook | Effect |
|---|---|
| `guard-paths` | Blocks edits to secret and signing files (for example `.env`, keystores, `google-services.json`) and to `infrastructure/prod/` |
| `guard-shell` | Blocks pushing to `main`, force pushes, merging or approving a PR, real Azure provisioning, and store-credential commands |
| `guard-outbound` | Blocks outbound messaging and publishing tools; agents save drafts and a founder sends them |
| `format-on-edit` | Formats edited files when a formatter is installed |

**Non-negotiable rules** that agents and humans both follow include millimetres internally, no invented numeric geometry by the model, no secrets or real photos or body measurements in the repo, no guarantee language ("perfect fit", "precision AR", "100% accurate"), and contract-first changes to API shapes [S6 `CLAUDE.md`].

**Limits of this method, stated honestly.** These controls are written down and the hooks exist. CI workflows reached `main` on 1 Nov (PR #6), but CI Benchmarks failed there until PR #19, which was still open [S10]. The `needs-human` label did not exist in the repository on 28 Oct [S8 audit] and L0 still listed it as open on 1 Nov [S10]. The "agents never merge or approve" rule is a hook that blocks specific commands (PR merge and approve commands, pushes to `main`), not a GitHub permission [S6 `guard-shell.mjs`; S11], so it does not stop a person or another tool. On 1 Nov all 14 merges were made from one founder account with no approving review [S10]. The review layer is therefore the X1 and X2 agent reviews plus founder judgement, and `[FOUNDER INPUT NEEDED: why approvals were removed and how review is now done]`. Agent output is a draft until a human has checked it.

### 2.5 Wave 1 of agent work

On 28 Oct 2026 the lead agent (L0) reported 14 agents running in parallel, each in its own worktree and branch [S8 digest]. By 1 Nov, 14 PRs had been merged to `main` (list in Section 2.1) and 13 were open at L0's snapshot (15 on 2 Nov) [S10; S13]. L0's 1 Nov digest records, for the merged work [S10]:

- The K1 contract is `1.0.0-draft.2`, a draft that is not frozen.
- The N5 recipe `woven_shirt_crop_v1` is `status: draft`; no sewist or supervisor has been named as reviewer.
- N3's ease ranges (PR #20, open) are unverified placeholders.
- X1 reviewed several merged PRs and agents replied with fixes; L0 saw no X1 re-review after the fixes.
- X2 rated D9's site and outreach drafts (#7) Blocked, with 7 blocking issues, after they had merged; this report (#8) and the video script (#13) were also rated Blocked.
- CI Benchmarks was failing on `main` (a missing `jsonschema` dependency, so the constraint suite did not run on `main`); PR #19 fixes it and was open.

On a branch, PR #19 reports the constraint suite at 27 cases and 29 checks on synthetic inputs: false acceptance 0/21, correct rejection 21/21, correct acceptance 8/8, false rejection 0/8, indeterminate 0/29 [S10]. These are synthetic-input results from an unmerged branch and say nothing about a real garment. The suite has grown past the 24 cases named as the blueprint target [S10; S3 §17.2]. `[UPDATE AS OF the status date: list PR numbers merged since 1 Nov.]`

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
| **P0 gate is red.** On 28 Oct, L0 found 0 of 5 exit-evidence items in the repository. On 1 Nov, L0 kept the rating RED: the proposed P0 window ended 1 Nov, the repo holds no physical make record, the recipe is still a draft, and the founders had not answered L0's physical-progress questions | [S8 audit; S10] | P0 did not pass by its proposed exit date: 0 of 5 exit-evidence items fully met (4 partial, 1 absent) [S10]. The blueprint's rule applies now: demonstration mode, no library expansion, and a documented re-plan, which L0 recommended recording and the founders had not [S3 §12; S10] |
| Scope was still being reconciled on 21–22 Oct; decisions D01–D13 are all open | [S2 §14; S3 §20; S8 `docs/decisions.md`] | A draft recipe and engine merged on 1 Nov without D01 being agreed. The recipe stays `draft` until D01 and the sewist review (H-01, H-02) are done [S10 `human-tasks.md`] |
| CI workflows were added on 1 Nov (PR #6). CI Benchmarks is failing on `main`; no `needs-human` label | [S8 audit; S10] | The constraint suite has not run on `main`. The fix, PR #19, was still open on 2 Nov `[AS-OF DATE]` |
| Code-owner reviews were blocked for single-owner areas, and collaborator invites were pending on 28 Oct. By 2 Nov the GitHub API listed all three founders as collaborators with no pending invitations | [S7 body; S14] | Backup owners merged (PR #1) |
| Imagine Cup 2027 rules and deadline are unverified; the cited competition date is tentative | [S1 slide 13; S3 §12 note] | The internal 7 Jan 2027 date may not match the competition |
| Founders' answers on physical progress (shirt, measurements, trial, reviewer) were still outstanding on 1 Nov | [S10] | P0 status cannot be raised above red in this report |
| Ethics, consent and deletion route for user sessions is not yet confirmed with the supervisor | [S10 `human-tasks.md`, H-05; S3 §20 D12] | Participant recruitment cannot start until it is |
| `[FOUNDER INPUT NEEDED: other obstacles such as time clashes with other modules, access to materials, tool or budget limits.]` | | |

---

## 3. Future work

### 3.1 In progress

As of 1 Nov 2026, wave-2 work is open as PRs: CI fix (#19), fit and ease module (#20), calibration and overlay (#21), API connected to the contract and engine (#22, draft), AI pipeline connected to the contract and engine (#23), cut guide and DIY steps (#24), Design Studio screens (#25), P0 make kit and record template (#17), security documents (#18) and mobile QA (#32) [S10; S13]. They map to the P0 exit evidence as follows [S8 audit; S10]:

| P0 exit evidence | State on `main`, 1 Nov 2026 |
|---|---|
| Approved JSON/OpenAPI fixture | Contract `1.0.0-draft.2` merged, **draft, not frozen** (#15) |
| Real structured response, logs, failure handling | API scaffold and AI pipeline skeleton merged (#5, #10); connected versions open (#22, #23); no live Azure trace (access and cap unconfirmed, H-11); `deploy-staging` has 0 runs |
| Unit tests and a dimensioned cut plan | Feasibility engine and constraint suite merged (#12, #9); the suite has not run on `main` because CI Benchmarks is failing, and the fix #19 was open on 2 Nov |
| Installable build / end-to-end mock path | Expo scaffold with intake screens 1–4 on fixtures merged (#14); no `eas.json`, device and EAS account unconfirmed (H-06) |
| Photo and measurements of the outcome | No record in the repo; make kit and template in open PR #17 |

X1's review of the open PR #22 (API connected to the contract and engine) reports 3 critical and further major issues, for example a superseded revision still returning its cut plan, so that work is not complete or merged. X1 also reported major issues on #24 (cut guide and DIY steps) `[X1 comment on #22 read 2 Nov; #24 findings per the project lead, not re-read here]`.

`[UPDATE AS OF the status date: replace this table with the actual state of each item.]`

### 3.2 To do (planned)

The following are **planned**, not done. Order follows the blueprint's critical path: garment data contract, real measurements, pattern rule correctness, backend check API, app confirmation, accurate cut guide, physical make, evaluated evidence [S3 §13.1].

1. **Finish P0 (planned; the proposed window ended 1 Nov 2026):** agree the first recipe (D01), name the sewist reviewer, measure a real shirt, mark and trial a cut, record the deviation in mm, and complete the five exit-evidence items. L0 proposes 4 Nov for the first make (H-04), up from 1 Nov [S3 §12; S10 `human-tasks.md`, H-01 to H-04].
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

P0 did not pass by its proposed date, so the blueprint's rule applies now: demonstration mode and no expansion of the transformation library until it passes, with a documented re-plan [S3 §12; S10]. The re-plan has not been recorded (L0 recommended it, with 4 Nov proposed for the first make). Build work continues in open PRs (fit, calibration, Design Studio, cut guide) but adds no garments or transformations [S10]. Tee and accessory work are conditional on the primary gate staying green [S3 §12 P2]. Marketplace requests and quotes come only after a validated design record exists [S3 executive position].

### 3.4 Risks to the plan

The blueprint's risk register rates pattern validity and three-person overload as critical, and photo calibration, jersey stretch, AI image mismatch, service access and cost, instruction safety, privacy and the submission schedule as high [S3 §19]. L0 copied these into a risk register, merged in PR #2 [S8 `docs/risk-register.md`].

### 3.5 Needs-human items

Work agents may only prepare, and that is listed for L0 [S10 `human-tasks.md`]. Items relevant to this report: H-10 (review this draft, record the video, complete the NTU GAI declaration form, submit by 10 Nov 2026), H-05 (supervisor ethics and consent route; the earlier H-08 was merged into it [S10]), and the `[FOUNDER INPUT NEEDED]` items above.

---

## 4. Conclusion

**Assessment as of `[AS-OF DATE]` (draft written 1 Nov 2026).** The project has a narrow, documented scope and design, and a first body of draft code on `main`, but no physical evidence and a P0 gate rated red.

- **Done:** scope V0.2, the blueprint, an advisor deck, a small directional survey [S1; S2; S3]. On 1 Nov, 14 PRs merged to `main` with draft work in every area: contract, feasibility engine, constraint suite, API and AI skeletons, infrastructure and CI, mobile intake screens on fixtures, and research and site drafts [S10; S13].
- **Not done:** the contract is a draft, the recipe is a draft with no reviewer recorded in the repository, and the repository holds no live AI trace, no build evidence and no physical-make record [S10]. As of 1 Nov, L0 rates P0 red, and the proposed window ended on that date [S10; S3 §12]. `[FOUNDER CONFIRM: No physical make has been reported.]` If one exists off the repository, it changes the fifth exit-evidence item and this paragraph.
- **Not claimed:** no feasibility accuracy, rejection rate on real garments, overlay error, usability result or cost figure exists. The constraint-suite counts on PR #19 are synthetic inputs on an unmerged branch. Survey figures are directional only, and the worked example is illustrative [S1 slides 2, 8; S10].
- **What decides the next phase.** If P0 later closes (one measured shirt, a reviewed dimensioned cut plan, a physical trial with deviation recorded), the plan can proceed to the connected alpha. P0 did not pass by its proposed date, so the blueprint's rule applies now: demonstration mode and no library expansion until it passes. The documented re-plan §12 requires is still open (L0 recommended it; not recorded as of its 1 Nov digest). Build work continues in open PRs but adds no garments or transformations [S3 §12, §19.1; S10]. If the make slips past the status date, this report says it has not been done.
- **Schedule.** The internal plan compresses build, user sessions and four physical makes into 22 Oct 2026 – 7 Jan 2027, with P0 already late [S3 §12; S10]. The NTU final report is not due until April 2027 [S5], so the NTU schedule has slack that the internal one lacks. `[FOUNDER INPUT NEEDED: confirm which schedule governs, and agree with the supervisor.]`
- **Method.** The governance model is written down and partly enforced by hooks, but its first real use was 14 merges in two minutes from one account with no approving review, followed by X2 audits that rated several merged or open PRs Blocked [S10]. That shows the audit step finds problems, and also that it can run after merge. Whether the model works in practice is not yet established. Every geometry rule, recipe and claim still needs human review and a physical test before it counts as evidence [S6 `CLAUDE.md`; S3 §8.2].

`[UPDATE AS OF the status date: revise this assessment against the real P0 result.]`

---

## References

Internal documents are listed in `SOURCES.md` under tags S1–S14. External references quoted from those documents:

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
| Used for in the project | Writing code, tests, documentation and drafts under the agent roles in Section 2.4. Work since branch protection was enabled enters `main` through a PR merged from a founder's GitHub account, which agents also use `[FOUNDER CONFIRM: who ran the 14 merges]`; as of 1 Nov GitHub requires no approving review [S11; S12] |
| Used for in this report | Drafting structure and text from the source documents and repository (agent X3, Report Writer). Factual claims are tagged to a source in `SOURCES.md`; judgments in the Conclusion are the drafter's |
| Human input | `[FOUNDER INPUT NEEDED: who wrote each source PDF (scope, blueprint, advisor deck), and was AI used in writing them?]` Founders also supply the physical and user-research facts marked `[FOUNDER INPUT NEEDED]` and review the draft |
| Not delegated | Sewing and measuring, participant contact, consent, accounts, credentials, submissions and approvals are human-only [S6 `CLAUDE.md`] |
| Data given to the tools | Project rule: synthetic or consented data only; no secrets, real user photos or body measurements in the repository, prompts or logs [S6 `CLAUDE.md`, rule 7]. `[FOUNDER CONFIRM this held]` |
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
11. Final status of PRs and the P0 result, to replace the `[UPDATE AS OF the status date]` markers.
12. One shared status/evidence-freeze date for this report and the video script (v0.1 said 9 Nov; the video's shot list says 6 Nov; neither is chosen here).
13. Why approvals were removed on `main`, when, and how review is now done.
14. Dr Wesley's role; which phase dates (blueprint or deck) apply to P3 and P4.
