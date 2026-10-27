# FYP interim video: shot list (draft v0)

Status: all shots are **PLANNED**. Nothing has been filmed or recorded. Owner column names the founder who captures it; the agent only prepares this list.

Recording window proposal: film 4 to 7 Nov 2026, edit 8 to 9 Nov, submit by 10 Nov 2026 (proposed, not agreed). Buffer is thin: see README risks.

## A. Real-world footage (needs a human with a camera)

| ID | Shot | Details | Owner | Consent / privacy | Status |
|---|---|---|---|---|---|
| A1 | Real shirt, top-down, flat on a table | The same oversized woven button-up that will be used for the P0 trial, if chosen. Tape measure, ruler and chalk in frame. Daylight, no faces. Hold 10 s. | Narthananilaa (shirt choice), Delfine (camera) | Shirt owner confirms OK to publish | planned |
| A2 | Close-up of ruler on the shirt, chalk cut mark | Show the mark and the ruler reading. Only film a mark that is really measured. If P0 trial not done, film marking a practice line on spare fabric and label "practice mark". | Narthananilaa | none beyond A1 | planned |
| A3 | Founders closing shot | Each founder says one line from S4, or voice-over over A1. Faces only with written consent from that founder. | All | Founder consent noted in the consent log | planned |
| A4 | Title and credits plate | Static cards, no filming. | Delfine | none | planned |
| A5 | (Variant B only) Before and after of the made garment | Same framing, same scale marker, ruler visible in both. Predicted vs measured table follows. | Narthananilaa | Garment owner consent | planned, depends on P0 make |

## B. Screen recordings from the repo (can be captured by Kireeti)

| ID | Shot | Details | Owner | Privacy | Status |
|---|---|---|---|---|---|
| R1 | Repo root and folder tree | `apps/`, `services/`, `packages/`, `content/`, `tests/`, `docs/`. Show the README or CLAUDE.md headings only. | Kireeti | Private repo: hide browser profile, tokens, notifications | planned |
| R2 | Agent definitions and hooks | `.claude/agents/` (29 files) and `.claude/hooks/` file names. Do not open any hook that references secrets paths. | Kireeti | check no secrets in frame | planned |
| R3 | Pull request list | Show open and merged PRs on `main` protection: one code-owner approval needed. SLOT-1 depends on what is merged by then. | Kireeti | Redact reviewer emails | planned |
| R4 | Test or benchmark run | Only if N1/N2 PRs are merged and tests really run. Show command and the final "x passed" line with the total. | Narthananilaa | none | planned, conditional |

## C. Props and paper shots (can be captured at a desk)

| ID | Shot | Details | Owner | Status |
|---|---|---|---|---|
| P1 | Hand-drawn shirt front with the crop sum | 780 / 500 / 30 / 530 / 250 mm written in marker. Tag illustrative. | Narthananilaa | planned |
| P2 | Chalk-line pass over a printed layout | optional | Narthananilaa | planned |
| P3 | Rejection card, redrawn | Paper or digital card: request, reason in mm, alternative. Tagged illustrative. | Delfine | planned |

## D. App screens (mock-ups unless real build exists)

| ID | Screen | Source | Label | Status |
|---|---|---|---|---|
| M1 | Garment capture (flat-lay, front and back) | D2 design, Figma | MOCK-UP | planned |
| M2 | Measurement guide with sample values | D2 design | MOCK-UP, SAMPLE DATA | planned |
| M3 | Result card with status badge, fewer than three options | D3 design | MOCK-UP | planned |
| M4 | Cut guide with ruler checkpoint (fallback diagram) | D4 design | MOCK-UP | planned |
| M5 | (Only if an installable build exists) screen recording on a real Android device | D6 | label by what is real: "prototype build" only if connected to the real engine, else MOCK-UP | planned, conditional |

## E. Graphics (can be produced without filming)

| ID | Graphic | Source | Status |
|---|---|---|---|
| G1 | Four survey stats cards, footer with n = 25 | Scope V0.2 section 01 | planned |
| G2 | Three-step journey diagram | Advisor deck slide 1 | planned |
| G3 | "AI proposes, engine checks" split | Advisor deck slide 7 | planned |
| G4 | Coverage ladder, three levels | Advisor deck slide 4 | planned |
| G5 | Phase bar P0 to P4, "internal, provisional" | Advisor deck slide 13 | planned |
| G6 | "Research: planned" card | this folder | planned |
| G7 | "P0 status: red" card | L0 status | planned |
| G8 | Architecture sketch, boxes tagged proposed | Advisor deck slide 11 | planned |
| G9 | Evidence plan table with empty Result column | Advisor deck slide 12 | planned |

## needs-human items from this shot list

1. Choose and confirm the shirt and its owner's publish consent (A1).
2. Operate the camera, ruler and chalk, and record real measurements (A1, A2, A5). The agent cannot do this.
3. Record narration and decide who is on camera (A3).
4. Confirm the NTU video length limit and file format with the supervisor.
5. Put raw footage in a shared drive outside the repo; record the licence of any music or font.
6. Sign off captions.
