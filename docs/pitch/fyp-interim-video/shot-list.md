# FYP interim video: shot list (3:00 summary, draft v1)

Status: all shots **PLANNED**. Nothing has been filmed. Owner = founder who captures it.

Schedule: status date is 9 Nov 2026, shared with the report (#8). Script approval, filming and editing must all finish before submission on 10 Nov. Maximum video length 3:00.

## A. Real-world footage (needs a human with a camera)

| ID | Shot | Details | Owner | Consent / privacy |
|---|---|---|---|---|
| A1 | Stand-in shirt flat on a table | Any spare woven shirt, tape, ruler, chalk. Caption "stand-in shirt, not the trial shirt": the trial shirt is not chosen. Daylight, no faces. 6 s. | Delfine | Shirt owner OK to publish |
| A3 | Founders closing shot | One line each, or voice-over. Faces only with written consent. | All | Consent log |
| A4 | Title and end plates | Static cards. | Delfine | none |

## B. Screen recordings from the repo (Kireeti)

| ID | Shot | Details | Privacy |
|---|---|---|---|
| R1 | Repo root and folder tree | `apps/`, `services/`, `packages/`, `content/`, `tests/`, `docs/`. | Hide browser profile, tokens, notifications |
| R2 | Agent definitions and hooks | `.claude/agents/` (29 files), `.claude/hooks/` file names only. | No secrets in frame |
| R3 | Pull request list | Merged list (14 on 1 Nov, 11 on 9 Nov, incl. #22); `main` requires a PR, 0 required reviews. As-of date on screen. | Redact reviewer emails |
| R4 | CI result on `main` | CI Benchmarks log lines "27 cases, 29 checks (synthetic inputs)" and "exact status+code match 29/29" from `main` (8b6faa5 on 9 Nov). Re-check green on recording day. | none |

## C. App screens (all demo-only, mock data)

| ID | Screen | Label | Notes |
|---|---|---|---|
| M1 | Intake screens (`apps/mobile/app/(intake)/`, #14) | PROTOTYPE, SAMPLE DATA | Capture on web or an emulator and caption how. If captured on the S24 Ultra, change S4b first, because a phone run would then exist. Do not film the entry screen unless #33 has merged: on main it still says "get redesigns that passed the checks we run" |
| M3 | Result card with status badge (#25) | PROTOTYPE, SAMPLE DATA | MOCK DATA badge in frame; say "Verified is sample text" aloud |
| M4 | Cut guide, dimensioned diagram (#24) | PROTOTYPE, SAMPLE DATA | Diagram only, no overlay. Do not film the edit-then-cut path |

## D. Graphics (no filming)

| ID | Graphic | Source |
|---|---|---|
| G1 | Two survey stat cards, 24/25 and 17/25, footer with n = 25, October 2026, university students and friends, directional | Scope V0.2 section 01; C-40 |
| G2 | Three-step journey diagram | Advisor deck slide 1 |
| G3 | "AI proposes, engine checks" split | Advisor deck slide 7 |
| G7 | "Next" card (one real shirt, planned) | C-16 |
| G10 | "NOT DONE" checklist card with the 9 Nov status date | C-41, C-42, C-16, C-20, C-21 |
| G11 | Imagine Cup card: deadline, legal entity required, no eligibility claim | C-43 |

## needs-human

1. Film A1, A3; record narration; decide who is on camera.
2. Confirm the Samsung S24 Ultra and Expo build service wording (S4b) and "I ran all 25 merges after approving each batch" (S5).
3. Confirm the NTU length limit (3:00 per Kireeti) and file format with the supervisor.
4. File the NTU generative AI declaration.
5. Raw footage outside the repo; music and font licences; caption sign-off.
