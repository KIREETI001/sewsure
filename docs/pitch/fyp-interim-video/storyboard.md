# FYP interim video: storyboard (3:00 summary, draft v1)

Status: DRAFT. Every visual is **PLANNED** unless the Evidence column names a repo path or document that exists today. Nothing has been filmed. Runtime about 2:48 (estimate at 140 wpm, an assumption); maximum 3:00. Narration: `narration-script.md`. Shots: `shot-list.md`. Claim IDs: `../claims-register.md`. Replaces the 10-minute storyboard of commit `331ffe5`.

## On-screen label rules (apply to every scene)

- Corner tag on every screen capture: `MOCK-UP`, `PROTOTYPE, SAMPLE DATA`, `RECORDED FROM REPO`, `PLANNED`, `REAL FOOTAGE`, `SURVEY, n = 25, DIRECTIONAL` or `STATUS AS OF 9 Nov 2026`. One per shot, never none.
- Any number on screen carries a lower-third source line, for example `Source: team survey, n = 25, directional only`.
- App screens keep the MOCK DATA badge in frame. Do not show the edit-then-cut path (it ends at "could not find that version").
- No body measurements of a real person, no faces or real user photos (non-negotiable 7); founders appear only with recorded consent.

## Scenes

| # | Time | Speaker | Visual | Label | Evidence today | Shots |
|---|---|---|---|---|---|---|
| 1 | 0:00 to 0:11 | D | Stand-in shirt flat on a table, ruler and chalk beside it. Title card: "SewSure. FYP interim summary. 10 Nov 2026." | REAL FOOTAGE (planned); caption "stand-in shirt, not the trial shirt" | none yet | A1, A4 |
| 2 | 0:11 to 0:27 | D | Two numbers appear: 24/25 and 17/25 with plain captions. Footer: "Team exploratory survey, October 2026, n = 25 university students and friends. Not representative. Directional only." | SURVEY, n = 25, DIRECTIONAL | Scope V0.2 section 01; deck slide 2 (C-01, C-02); sample description C-40 | G1 |
| 3 | 0:28 to 0:59 | K | Three-step graphic (photograph and measure, redesign options checked, cut guide or tailor brief), then two boxes: "AI proposes from approved recipes" and "Feasibility engine checks, in mm; meant to be the only thing that sets status". | PLANNED / CONCEPT DIAGRAM | deck slides 1, 7 | G2, G3 |
| 4 | 0:59 to 1:14 | N | CI log capture from `main`: "27 cases, 29 checks (synthetic inputs)". Card: "Synthetic cases, not a measured shirt." | RECORDED FROM REPO | CI Benchmarks on `main` at 8b6faa5, 9 Nov (C-08) | R4 |
| 5 | 1:14 to 1:17 | K | PR list showing #22 merged ("API calls the engine"). | RECORDED FROM REPO | #22 merged 9 Nov (C-39) | R3 |
| 6 | 1:18 to 1:26 | D | Quick screen recording of merged intake and result-card screens, MOCK DATA badge in frame, "Verified within supported checks" visible; caption "Verified = sample text". | PROTOTYPE, SAMPLE DATA | `apps/mobile/` on `main` (#14, #25); X1 9 Nov (C-20) | M1, M3 |
| 7 | 1:27 to 1:55 | N then D | Plain checklist card "NOT DONE" (as of 9 Nov 2026): no physical make; shirt not chosen; no sewist review (recipe is a draft); phase 0 not passed; cut guide is a diagram only, no overlay; no phone run; no interviews yet. One-second cut guide diagram (M4) under "diagram only". | STATUS AS OF 9 Nov 2026 | C-41, C-42, C-16, C-20 | G10, M4 |
| 8 | 1:56 to 2:02 | K | Same card, two more lines: "AI pipeline not connected to the API"; "Azure not set up". | STATUS AS OF 9 Nov 2026 | C-41, C-21 | G10 |
| 9 | 2:03 to 2:26 | K | Repo folders, `.claude/agents/` (29 files), `.claude/hooks/`, then PR list: "14 merged 1 Nov, 11 merged 9 Nov". On-screen text: "main requires a PR; no approval required." | RECORDED FROM REPO | commit `84efce5` onwards; GitHub PR list 9 Nov (C-09, C-10, C-39, C-44) | R1, R2, R3 |
| 10 | 2:26 to 2:33 | N | Card: "Next: one real shirt, a measured cut plan, an honest comparison. Planned." | PLANNED | none (plan) | G7 |
| 11 | 2:34 to 2:44 | K | Card: "Imagine Cup 2027: deadline 28 Feb 2027, official Rules. Legal entity required. We are not claiming eligibility." | PLANNED | C-43, not opened by D8 | G11 |
| 12 | 2:44 to 2:47 | all | Founders to camera or voice-over; last frame: team names, "Interim summary, FYP 2026 S1", "Targets are not results." | REAL FOOTAGE (planned) | none yet | A3, A4 |

Removed from the 10-minute cut: the illustrative crop sum and peplum rejection card, the physical-make variant (Variant P), the phase bar, the architecture sketch and the evidence-plan table. None assumed a make that has happened.

## Accessibility and captions

- Burned-in captions on all narration (needs-human: final caption check). Readable at phone size; no information by colour alone.
- No media files are committed to the repo. Editor, music licence and raw-footage store are needs-human.
