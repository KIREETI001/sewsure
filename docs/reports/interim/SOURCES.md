# Sources for the interim report draft

Maps each factual claim in `interim-report.md` to its source. Retrieved and read 28 Oct 2026. Source PDFs are in the founders' parent folder (outside this repo) and are not copied here.

## Source list

| Tag | Source | Location / version |
|---|---|---|
| S1 | SewSure Advisor Presentation, 14 slides, "Prepared for Dr Wesley, 22 October 2026, proposed plan, not results" | `SewSure_Advisor_Presentation.pdf` |
| S2 | SewSure Product Scope & Feature Definition, Source of Truth V0.2, 22 Oct 2026 | `SewSure_Source_of_Truth_Product_Scope_V0.2.pdf` |
| S3 | SewSure Technical Implementation Blueprint & Three-Person Delivery Plan V0.1, 22 Oct 2026 | `SewSure_Technical_Implementation_and_3_Person_Plan_V0.1 (1).pdf` |
| S4 | NTU EEE, Suggested Format of FYP Interim Report | `SuggestedFormatInterimReport.pdf` |
| S5 | NTU EEE Final Year Project page, deadlines table (printed 22 Oct 2026) | `fyp deadlines.pdf` |
| S6 | This repo on `main@84efce5` (root `CLAUDE.md`, `.claude/agents/`, `.claude/hooks/`, `.github/CODEOWNERS`) | git |
| S7 | GitHub PR #1, "Add backup code owners for each area" (open on 28 Oct 2026) | `gh pr view 1` |
| S8 | GitHub PR #2, L0 baseline audit, `docs/digests/2026-10-28-baseline-audit.md`, `2026-10-28.md`, `human-tasks.md`, `docs/risk-register.md`, `docs/decisions.md` (open on 28 Oct 2026, not yet on `main`) | branch `l0/wave1-baseline-digest` |
| S9 | `docs/CLAUDE.md` documentation rules | git, `main` |

S8 content is L0's own report and is unreviewed until PR #2 is merged.

## Claim map

| Report section | Claim | Source |
|---|---|---|
| Header | Interim report due 10 Nov 2026 to supervisor and examiner, with video | S5 |
| Header | FYP 2026 S1, Aug 2026 – May 2027 | S5 |
| Header | Supervisor named Dr Wesley | S1 slide 1 |
| 1.1 | Unused garments, skill gap, image is not feasibility | S1 slide 2 |
| 1.1 | App flow and up to three ranked redesigns | S2 §01; S1 slide 1 |
| 1.1 | Survey 24/25, 17/25, 21/25 | S1 slide 2; S2 §01 |
| 1.1 | Survey 12/25 would consider a tailor | S2 §01 |
| 1.1 | Survey is small, non-representative, directional; does not show willingness to pay or accuracy | S1 slide 2; S2 §01 |
| 1.1 | Competitor observations unverified | S1 slide 3 |
| 1.2 | "AI proposes, deterministic engine checks" | S1 slide 7 |
| 1.2 | Model picks allow-listed recipe IDs; no invented geometry | S6 `CLAUDE.md` rule 4; S3 §4.1 |
| 1.3 | Levels 1–3 and accessory pilot | S2 §03; S1 slide 4 |
| 1.3 | Core features, no payments | S2 §05, §08, §09, §11 |
| 1.3 | AR, try-on, 3D are stretch/future | S2 §07, §08 |
| 1.3 | Non-claims on fit, screen line vs fabric | S2 §03, §08 |
| 1.4 O1 | P0 pass criterion | S3 §12 |
| 1.4 O2 | P1 connected alpha | S3 §12; S1 slide 14 |
| 1.4 O3 | Design states, immutable revisions, no unverified safe-to-cut | S6 `CLAUDE.md` rules 2, 3, 5; S3 §1.1 |
| 1.4 O4 | 24 cases, 4 makes, 8–12 participants, 2–3 makers proposed | S1 slide 12; S3 §17.2, §20 D12 |
| 1.4 | No agreed numeric thresholds | S1 slide 12; S2 §12 |
| 1.4 | Blueprint objectives need student and supervisor approval | S3 cover |
| 1.5 | P0–P4 windows and exit evidence | S3 §12 |
| 1.5 | Dependency gate | S1 slide 13 |
| 1.5 | NTU dates: 14 Sep and 10 Nov 2026 | S5 (clear in extraction) |
| 1.5 | 25 Mar, 9 Apr, 12–16 Apr, 10–12 May, 19 May 2027 | S5, **inferred**: the table text extraction is scrambled, so each date was assigned to a row by matching the pattern of the FYP 2025 S2 column. Marked "confirm" in the report |
| 1.5 | Imagine Cup dates unverified; 7 Jan is internal | S1 slides 11, 13; S3 §12 note, §20 D13 |
| 2.1 | 21 Oct meeting; two sets of minutes; V0.2 dated 22 Oct | S2 cover, §15 |
| 2.1 | Deck and blueprint dated 22 Oct | S1 slide 1; S3 cover |
| 2.1 | One commit on `main` 28 Oct 2026; 29 agents; hooks; CODEOWNERS | S6 (`git log`: 84efce5, 2026-10-28; `ls .claude/agents`) |
| 2.1 | Branch protection: PR + one code-owner review | S8 audit ("What exists on main") |
| 2.2 | Source precedence rule | S2 §02 |
| 2.2 | Decision register mostly unresolved | S2 §14; S3 §20; S8 `docs/decisions.md` (all open) |
| 2.3 | Architecture, design record, AI boundary, gates, cut guidance | S1 slide 11; S3 §2, §3, §4.1, §4.3, §5.4, §5.5, §6; S2 §08 |
| 2.3 | Worked example illustrative | S1 slide 8; S3 §5.3 |
| 2.4 | Owner table and paths | S6 `CLAUDE.md` |
| 2.4 | 29 agents: L0, K1–K8, N1–N7, D1–D9, X1–X4 | S6 `.claude/agents/`; `CLAUDE.md` |
| 2.4 | X3 may edit only `docs/reports/`, `docs/adr/` | S6 `.claude/agents/x3-report-writer.md` |
| 2.4 | Process rules 1, 3, 4, 5 | S6 `CLAUDE.md` "How agents work here" |
| 2.4 | `main` protection, admins included; backup owners | S7 body; S8 audit |
| 2.4 | Four hooks and their effects | S6 `.claude/hooks/guard-paths.mjs`, `guard-shell.mjs`, `guard-outbound.mjs`, `format-on-edit.mjs` |
| 2.4 | Non-negotiable rules | S6 `CLAUDE.md` |
| 2.4 | No CI; no `needs-human` label | S8 audit |
| 2.5 | 14 agents running, 15 queued on 28 Oct | S8 daily digest, and the task brief given to X3 |
| 2.5 | Only PRs #1 and #2 open | `gh pr list`, 28 Oct 2026 |
| 2.6 | Questions Q1–Q4 on physical work | S8 audit |
| 2.6 | Keep denominators and negative results | S9 |
| 2.7 | Page counts (scope 10, blueprint 21) | S2 footer; S3 footer |
| 2.8 | P0 gate red, 0 of 5 items, 4 days left | S8 audit |
| 2.8 | Invites and owner blocking | S7 body |
| 2.8 | Ethics/consent route open (H-08, D12) | S8 `human-tasks.md`; S3 §20 D12 |
| 3.1 | P0 exit-evidence mapping and wave-1 agent areas | S8 audit table |
| 3.2 | Planned phases, critical path, fallback order, gate G4 | S3 §12, §13.1, §17.2, §18.3, §19.1; S8 `human-tasks.md` |
| 3.3 | V0.1 to V0.2 changes | S2 §13 |
| 3.3 | Demonstration-mode rule if gate fails | S3 §12 |
| 3.4 | Risk ratings | S3 §19; S8 `docs/risk-register.md` |
| 3.5 | H-08, H-10 | S8 `human-tasks.md` |
| 4 | All assessments | Derived from the rows above; the judgments ("tight", "slack") are the drafter's reading, to be confirmed by founders |
| App. A | GAI declaration is a student-submitted NTU form | S5 (links list "GAI declare form"); S9 |
| App. A | Commit trailer `Co-Authored-By` | repo commit convention given in the task brief |

## Unsourced items intentionally left as placeholders

Names and matric numbers, survey method and date, supervisor meetings, the 14 Sep project plan submission, all physical-make facts, interviews, Azure and device status, effort hours, other obstacles, academic references. All appear as `[FOUNDER INPUT NEEDED]` in the report.
