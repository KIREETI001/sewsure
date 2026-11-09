# Sources for the interim report draft

Maps each factual claim in `interim-report.md` to its source. Revised 9 Nov 2026 (v0.6, matching the report: Kireeti's individual report). Sources were first read 28 Oct 2026; GitHub facts were re-checked on 1, 2 and 9 Nov 2026. Source PDFs are in the founders' parent folder (outside this repo) and are not copied here.

## Source list

| Tag | Source | Location / version |
|---|---|---|
| S1 | SewSure Advisor Presentation, 14 slides, "Prepared for Dr Wesley, 22 October 2026, proposed plan, not results" | `SewSure_Advisor_Presentation.pdf` |
| S2 | SewSure Product Scope & Feature Definition, Source of Truth V0.2, 22 Oct 2026 | `SewSure_Source_of_Truth_Product_Scope_V0.2.pdf` |
| S3 | SewSure Technical Implementation Blueprint & Three-Person Delivery Plan V0.1, 22 Oct 2026 | `SewSure_Technical_Implementation_and_3_Person_Plan_V0.1 (1).pdf` |
| S4 | NTU EEE, Suggested Format of FYP Interim Report | `SuggestedFormatInterimReport.pdf` |
| S5 | NTU EEE Final Year Project page, deadlines table (printed 22 Oct 2026) | `fyp deadlines.pdf` |
| S6 | This repo on `main@c46c5d8` as of 2 Nov 2026 (scaffold commit `84efce5`; root `CLAUDE.md`, `.claude/agents/`, `.claude/hooks/`, `.github/CODEOWNERS`) | git |
| S7 | GitHub PR #1, "Add backup code owners for each area" (merged 1 Nov 2026, `bd4e24c`) | `gh pr view 1` |
| S8 | L0 baseline audit of 28 Oct 2026: `docs/digests/2026-10-28-baseline-audit.md`, `2026-10-28.md`, `docs/risk-register.md`, `docs/decisions.md` (PR #2, merged 1 Nov 2026, `c46c5d8`) | `main` |
| S9 | `docs/CLAUDE.md` documentation rules | git, `main` |

| S10 | L0 daily digest of 1 Nov 2026 and updated `human-tasks.md` (PR #26, merged 9 Nov 2026, `d656987`; written ~20:35 SGT on 1 Nov at `main@c46c5d8`, so its ratings are dated 1 Nov) | `docs/digests/2026-11-01.md` on `main` |
| S11 | PR #16, "Make PR approvals optional in the agent rules" (merged 1 Nov 2026, 10:16 UTC, `4adc272`) | `gh pr view 16` |
| S12 | GitHub branch-protection API for `main`, read 1 Nov 2026: PR required, `required_approving_review_count` 0, `require_code_owner_reviews` false, `enforce_admins` true | `gh api repos/KIREETI001/sewsure/branches/main/protection` |
| S13 | `gh pr list --state all`: on 1 Nov 14 merged (#1–#7, #9–#12, #14–#16), 13 open (#8, #13, #17–#26, #32); on 2 Nov 15 open (adds #33, #34) | GitHub |
| S14 | GitHub collaborators and invitations API for the repo, 2 Nov 2026: collaborators KIREETI001, vanilaa23, delfinee; 0 pending invitations | `gh api repos/KIREETI001/sewsure/collaborators` and `/invitations` |
| S15 | PR #22 (API connected to contract and engine, **merged 9 Nov**, `4dd121f`; earlier head `cbffff4`): X1 review at `b18d57f`; K2 reply 1 Nov (`cbffff4`); X1 recheck 2 Nov, comment 6568815203. Also PR #23 (AI code, still open on 9 Nov) | `gh pr view 22`, issue comments |
| S16 | PR #24 (cut guide and DIY steps, **merged 9 Nov**, `6c4630b`; earlier head `36bcda7`): X1 review at `ce545ab`; D4 reply 1 Nov (`36bcda7`); X1 recheck 2 Nov, comment 6568846312; `apps/mobile/src/make/gate.ts` at `36bcda7` always returns the diagram | `gh pr view 24`, issue comments |

| S17 | `gh pr list --state all` and `gh pr view` on 9 Nov 2026: merged 9 Nov (all by KIREETI001, 11:07–11:12 UTC): #19 `5490480`, #34 `a14203e`, #17 `d12c3e2`, #18 `e1dd074`, #26 `d656987`, #35 `34946dd`, #22 `4dd121f`, #24 `6c4630b`, #25 `1a3e11e`, #40 `128db02`, #41 `8b6faa5`; open: #8, #13, #20, #21, #23, #32, #33, #36 (draft), #37, #38, #39, #42, #43, #44 (draft). The statement that the merges followed Kireeti's explicit approval comes from the project lead's message, not from GitHub | GitHub; lead message of 9 Nov |
| S18 | GitHub Actions runs on `main` read 9 Nov 2026: CI Benchmarks and CI Python succeeded on `8b6faa5` (11:12 UTC); X2 reports the CI Benchmarks log shows 27 cases, 29 checks, 0/21, 21/21, 8/8, 0/8, 0/29 and 29/29 exact matches (I did not read the log myself); earlier runs on the same morning were cancelled by newer pushes. Branch protection API: 0 approving reviews required, `enforce_admins` true | `gh run list --branch main`; `gh api .../branches/main/protection` |
| S19 | X1 time-boxed rechecks on 9 Nov 2026: #22 at `7fb7198` (SQLite 73 passed, local PostgreSQL 16.2 41 passed, no merge blocker); #24 at `53076fd` (safe as demo-only code on mock data; D3/D4 mock mismatch); #25 at `6888b7f` (safe on mock data; "Verified" label shown with MOCK DATA; dead-end after edit). I read the comments, not the code, and ran nothing | PR issue comments |
| S20 | This repo on `main@8b6faa5`, 9 Nov 2026: `packages/contracts` version `1.0.0-draft.3`; `woven_shirt_crop_v1` `status: draft`; `docs/evaluation/physical-make-record.md` says no make has been recorded; no `apps/mobile/eas.json`; `docs/decisions.md` P-02 (re-plan) `open`; latest digest `docs/digests/2026-11-01.md` | git |
| S21 | Project Plan, Project No. A3126-261, "Design and build an industrial software or product for Microsoft Imagine Cup 2027", AY2026-27 Semester 1, 14 Sep 2026: students, supervisor Dr Tan Chee Wah Wesley, responsibility allocation, objective of at least 2 Microsoft AI services, tentative 8 Jan 2027 submission and 13 Feb 2027 training dates | source text `plan.txt` from the PDF (read 9 Nov) |
| S22 | Microsoft Imagine Cup 2027 Official Rules and Regulations, last updated 4 Nov 2026: §3 schedule, §4.1 and §4.2 eligibility, §7 and §8 Azure Subscription ID and services requirement (10 services, US$1.00 usage each, by 28 Feb 2027), §8 and §12.3 Stage 2 materials, deadline 23:59 CST on 28 Feb 2027 (read in `rules.txt`). | source text `rules.txt` |
| S23 | Kireeti's answers of 9 Nov 2026, relayed by the project lead: Azure, merges, approvals, shirt, measurements, make, reviewer, survey, research, device, effort, obstacles, data rule, final review, check-ins; and the facts that no legal entity exists and that agents wrote code under Kireeti's direction. Not independently verified against any document | lead message, 9 Nov 2026 |
| S24 | Imagine Cup FAQ, https://imaginecup.microsoft.com/en-us/support/faq, read by X2 on 9 Nov 2026 (not read by me) | web |

S8, S10 are L0's own reports. S10 is dated 1 Nov and was merged on 9 Nov; no later L0 rating is on `main`.

## Claim map

| Report section | Claim | Source |
|---|---|---|
| Header | Interim report due 10 Nov 2026 to supervisor and examiner, with video | S5 |
| Header | FYP 2026 S1, Aug 2026 – May 2027 | S5 |
| Header | Advisor deck is "Prepared for Dr Wesley"; role not stated, so shown as addressee with a confirm placeholder | S1 slide 1 |
| 1.1 | Problem statement (unused garments, skill gap, image is not feasibility) presented as the team's statement, not as measured fact; only measured figure is survey 24/25 | S1 slide 2 |
| 1.1 | App flow and up to three ranked redesigns | S2 §01; S1 slide 1 |
| 1.1 | Survey 24/25, 17/25, 21/25 | S1 slide 2; S2 §01 |
| 1.1 | Survey 12/25 would consider a tailor | S2 §01 |
| 1.1 | Survey is small, non-representative, directional; does not show willingness to pay or accuracy | S1 slide 2; S2 §01 |
| 1.1 | Competitor observations unverified | S1 slide 3 |
| 1.2 | "AI proposes, deterministic engine checks" | S1 slide 7 |
| 1.2 | Model picks allow-listed recipe IDs; no invented geometry | S6 `CLAUDE.md` rule 4; S3 §4.1 |
| 1.3 | Levels 1–3 and accessory pilot, described as targets; nothing validated yet | S2 §03; S1 slide 4; S10 (no physical make or validation record) |
| 1.3 | Core features, no payments | S2 §05, §08, §09, §11 |
| 1.3 | AR, try-on, 3D are stretch/future | S2 §07, §08 |
| 1.3 | Non-claims on fit, screen line vs fabric | S2 §03, §08 |
| 1.4 O1 | P0 pass criterion | S3 §12 |
| 1.4 O2 | P1 connected alpha | S3 §12; S1 slide 14 |
| 1.4 O3 | Design states, immutable revisions, no unverified safe-to-cut | S6 `CLAUDE.md` rules 2, 3, 5; S3 §1.1 |
| 1.4 O4 | 24 cases, 4 makes, 8–12 participants, 2–3 makers proposed | S1 slide 12; S3 §17.2, §20 D12 |
| 1.4 | No agreed numeric thresholds | S1 slide 12; S2 §12 |
| 1.4 | Blueprint objectives need student and supervisor approval | S3 cover |
| 1.5 | P0–P4 windows and exit evidence (blueprint dates) | S3 §12 |
| 1.5 | Deck shows P3 7–22 Dec and P4 23 Dec–7 Jan; blueprint shows P3 7–15 Dec and P4 16 Dec–7 Jan | S1 slide 13; S3 §12 |
| 1.5 | Dependency gate | S1 slide 13 |
| 1.5 | NTU dates: 14 Sep and 10 Nov 2026 | S5 (clear in extraction) |
| 1.5 | 25 Mar, 9 Apr, 12–16 Apr, 10–12 May, 19 May 2027 | S5, **inferred**: the table text extraction is scrambled, so each date was assigned to a row by matching the pattern of the FYP 2025 S2 column. Marked "confirm" in the report |
| 1.5 | Imagine Cup dates unverified; 7 Jan is internal | S1 slides 11, 13; S3 §12 note, §20 D13 |
| 2.1 | 21 Oct meeting; two sets of minutes; V0.2 dated 22 Oct | S2 cover, §15 |
| 2.1 | Deck and blueprint dated 22 Oct | S1 slide 1; S3 cover |
| 2.1 | Scaffold commit 28 Oct 2026; 29 agents; hooks; CODEOWNERS | S6 (`git log`: 84efce5, 2026-10-28; `ls .claude/agents`) |
| 2.1 | Branch protection on 28 Oct: PR + one code-owner review | S8 audit ("What exists on main") |
| 2.1 | By 1 Nov: 0 approving reviews required (one was seen on 28 Oct, so the change date is unknown), admins still need a PR; A0–A3 become guidance | S11; S12 |
| 2.1 | 14 PRs merged 18:16–18:18 SGT on 1 Nov, all from KIREETI001, no approving review; list and contents | S10 "Merged"; S13 |
| 2.1 | 13 PRs open on 1 Nov (L0 snapshot); 15 on 2 Nov | S13 |
| 2.2 | Source precedence rule | S2 §02 |
| 2.2 | Decision register mostly unresolved | S2 §14; S3 §20; S8 `docs/decisions.md` (all open) |
| 2.3 | Architecture, design record, AI boundary, gates, cut guidance | S1 slide 11; S3 §2, §3, §4.1, §4.3, §5.4, §5.5, §6; S2 §08 |
| 2.3 | Worked example: 76 cm shirt, 52 cm finished, 2 cm hem, cut mark at 54 cm, illustrative (blueprint §5.3 uses different numbers and is not used) | S1 slide 8 |
| 2.4 | Owner table and paths | S6 `CLAUDE.md` |
| 2.4 | 29 agents: L0, K1–K8, N1–N7, D1–D9, X1–X4 | S6 `.claude/agents/`; `CLAUDE.md` |
| 2.4 | X3 may edit only `docs/reports/`, `docs/adr/` | S6 `.claude/agents/x3-report-writer.md` |
| 2.4 | Process rules 1, 3, 4, 5 | S6 `CLAUDE.md` "How agents work here" |
| 2.4 | PR required including for admins; no approving review required as of 1 Nov; any founder can merge | S11; S12 |
| 2.4 | Backup owners | S7 body |
| 2.4 | Agent merge/approve limit is a hook on specific commands, not a GitHub permission | S6 `.claude/hooks/guard-shell.mjs`; S11 |
| 2.4 | Four hooks and their effects | S6 `.claude/hooks/guard-paths.mjs`, `guard-shell.mjs`, `guard-outbound.mjs`, `format-on-edit.mjs` |
| 2.4 | Non-negotiable rules | S6 `CLAUDE.md` |
| 2.4 | `needs-human` label missing on 28 Oct and still open on 1 Nov | S8 audit; S10 (`human-tasks.md` H-07b) |
| 2.1, 2.4 | Leads are first reviewers; GitHub does not require their approval | S6 `CLAUDE.md`; S12 |
| 2.3 | Cut overlay planned and not working; #24 uses the diagram because `points_px` is not returned; no overlay accuracy exists | S16; S10 |
| 2.5 | 14 agents running on 28 Oct (queued figure dropped) | S8 daily digest |
| 2.1 | 11 PRs merged 9 Nov, by KIREETI001, no approving review required; list; approval claim from the project lead | S17; S18 |
| 2.5 | State on 9 Nov: contract draft.3, recipe draft, API calls the engine (SQLite 73, local Postgres 41, not Azure), screens demo-only on mock data, make kit and empty template, CI passes, AI pipeline not connected, open PRs, D3/D4 mock mismatch, placket and 50 mm open | S19; S20; S17; S18; S15 |
| 2.5 | 1 Nov: Contract draft.2 not frozen; recipe `draft`, no reviewer; ease ranges unverified; X1/X2 outcomes; CI Benchmarks failure; PR #19 synthetic counts (27 cases, 29 checks, 0/21, 21/21, 8/8, 0/8, 0/29) | S10 |
| 2.6 | Questions Q1–Q4 on physical work | S8 audit |
| 2.6 | Keep denominators and negative results | S9 |
| 2.7 | Page counts (scope 10, blueprint 21) | S2 footer; S3 footer |
| 2.8 | L0's last P0 rating is RED dated 1 Nov, no later rating on `main`; P-02 re-plan open on 9 Nov | S10; S20 |
| 2.8 | CI Benchmarks fixed by #19, passing on 9 Nov | S18 |
| 2.8 | P0 red: 28 Oct 0 of 5 items in repo (4 days left); 1 Nov still RED, window ended; 0 of 5 fully met, 4 partial, 1 absent; §12 re-plan recommended by L0, not recorded | S8 audit; S10 |
| 2.8 | CI added in PR #6, Benchmarks failing on `main` | S10 |
| 2.8 | Invites pending on 28 Oct; by 2 Nov all three are collaborators, 0 pending (S10 still shows the 1 Nov snapshot with one pending) | S7 body; S14 |
| 2.8 | Ethics/consent route open (H-05, formerly H-08; D12) | S10 `human-tasks.md`; S3 §20 D12 |
| 2.8 | Founders' physical-progress answers outstanding | S10 |
| 3.1 | P0 evidence state on `main` on 9 Nov and open PRs | S20; S17; S18; S19; S8 audit table |
| 3.1 | #22 and #23 connect separately; the AI pipeline is not connected to the API; #22's proposer is rule-based | S15 |
| 3.1 | X1 findings and rechecks on #22 (3 critical at `b18d57f`; not safe to merge at `cbffff4`) and #24 (safe only as demo-only on mock data at `36bcda7`; 3 new major); both merged on 9 Nov after X1 rechecks at 7fb7198 and 53076fd. Not verified here: whether the fixes work (read from X1's comments only) | S15; S16 |
| 3.2 | Constraint suite: 24 cases proposed; 27 cases and 29 checks on PR #19's run (synthetic) | S3 §17.2; S10 |
| 3.2 | Planned phases, critical path, fallback order, gate G4 | S3 §12, §13.1, §17.2, §18.3, §19.1 |
| 3.2 | H-04 first make proposed for 4 Nov (was 1 Nov, missed) | S10 `human-tasks.md` |
| 3.3 | V0.1 to V0.2 changes | S2 §13 |
| 3.3 | Demonstration-mode rule if gate fails | S3 §12 |
| 3.3 | Tee and accessory conditional on primary gate; marketplace after validated design record | S3 §12 P2; S3 executive position |
| 3.4 | Risk ratings | S3 §19; S8 `docs/risk-register.md` |
| 3.5 | H-05, H-10 | S10 `human-tasks.md` |
| Header | Individual report by Kireeti; project A3126-261; supervisor named in the plan | S21; S23 |
| 1.1 | Survey run in October 2026 among university students and friends; questionnaire not available | S23 |
| 1.4 | Objective of at least 2 Microsoft AI services; Azure not set up | S21; S23 |
| 1.5 | Imagine Cup 2027 schedule (2 Nov 2026 to 28 Feb 2027 rolling, 23:59 CST deadline; expert review 1 to 12 Mar; interviews 16 to 31 Mar; judging April; May to June) | S22 |
| 1.5 | 7 and 8 Jan 2027 dates were tentative and are superseded | S3 §20 D13; S21; S22 |
| 1.5, 3.2 | Re-baselined phase windows P0 10 to 22 Nov through P4 15 to 28 Feb, and the 30 Nov entry decision | **Drafter's proposal**, not sourced; labelled proposed |
| 2.1 | 14 Sep Project Plan, allocation and objective; V0.1 not available; approval removal at Kireeti's request, date "by 1 Nov"; all 25 merges by Kireeti after approving each batch | S21; S23; S11 |
| 2.1, 2.9 | Fortnightly supervisor check-ins; no dates or advice supplied | S23 |
| 2.4 | Responsibilities now vs the Project Plan; reasons not recorded | S21; S6 `CLAUDE.md` |
| 2.6 | Shirt not chosen (planned type), no measurements, marking, cutting or sewing, no reviewer, no interviews, Azure not set up, Samsung S24 Ultra and EAS account active | S23; S20 |
| 2.7, 2.8 | Weekly meetings of about 3 to 4 hours; costs not recorded; no other obstacles | S23 |
| 2.9 | PRs #5, #6, #10, #15, #18, #19, #22, #35 and agents K1 to K6; #23 open; scaffold commit and #16 from Kireeti's account; agents wrote the code under Kireeti's direction | S17; S6; S11; S23 |
| 3.4 | Imagine Cup entry risks: entity founded on or after 2 Nov 2024, Azure Subscription ID and Microsoft for Startups account, 10 services with US$1.00 usage each, 2 to 3 minute demo, pitch deck, architecture overview; no entity exists | S22 §4.1, §4.2, §7, §8, §12.3; S23 |
| App. A | Data rule held; final review by Kireeti line by line | S23 |
| 4 | All assessments | Derived from the rows above; the judgments ("tight", "slack") are the drafter's reading, to be confirmed by founders |
| App. A | GAI declaration is a student-submitted NTU form | S5 (links list "GAI declare form"); S9 |
| App. A | Commit trailer `Co-Authored-By` | repo commit convention given in the task brief |
| App. A | Who wrote the source PDFs and whether AI helped is **not sourced**; left as a placeholder | none |
| App. A | "Synthetic or consented data only" stated as a project rule, not an observed fact | S6 `CLAUDE.md` rule 7 |

## Unsourced items intentionally left as placeholders

Names and matric numbers, survey method and date, supervisor meetings, the 14 Sep project plan submission, all physical-make facts, interviews, Azure and device status, effort hours, other obstacles, academic references. All appear as `[FOUNDER INPUT NEEDED]` in the report.
