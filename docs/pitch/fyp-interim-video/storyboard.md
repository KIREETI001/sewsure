# FYP interim video: storyboard (draft v0)

Status: DRAFT. Every visual below is **PLANNED** unless the Evidence column says a repo path or document that exists today. Nothing here has been filmed.

Runtime about 9:50 (re-timed 9 Nov, estimate at 140 wpm; see Totals in the narration script). Narration is in `narration-script.md`; film list is in `shot-list.md`; claim IDs resolve in `../claims-register.md`.

## On-screen label rules (apply to every scene)

- Corner tag on every screen capture: `MOCK-UP`, `PROTOTYPE, SAMPLE DATA`, `RECORDED FROM REPO`, `ILLUSTRATIVE NUMBERS`, `PLANNED`, `REAL FOOTAGE`, `SURVEY, n = 25, DIRECTIONAL` or `STATUS AS OF 9 Nov 2026`. Use exactly one per shot, never none.
- Any number on screen carries a lower-third source line, for example: `Source: team survey, n = 25, directional only`.
- No body measurements of a real person on screen. Garment measurements are fine. Body-profile screens use sample values labelled `SAMPLE DATA`.
- No faces, no real user photos (non-negotiable 7). Team members appear only with their consent, recorded in the consent log (needs-human).

## Scenes

| # | Time | Speaker | Visual (what the viewer sees) | Label | Evidence today | Shot ID |
|---|---|---|---|---|---|---|
| 0 | 0:00 to 0:25 | D | Slow top-down shot of a real oversized woven shirt on a table, ruler and tailor's chalk beside it. Title card: "SewSure. FYP interim presentation. 10 Nov 2026." | REAL FOOTAGE (planned) | none yet | A1, A2 |
| 1a | 0:25 to 1:20 | D | Four large numbers appear one at a time: 24/25, 17/25, 21/25, 12/25, each with its plain-words caption. Footer on all: "Team exploratory survey, n = 25. Small, non-representative sample. Directional only." | SURVEY, n = 25, DIRECTIONAL | Scope V0.2 section 01; Advisor deck slide 2. Raw export not in repo (see register C-01) | G1 |
| 1b | 1:20 to 2:45 | K | Three-step graphic: photograph and measure, redesign options checked, cut guide plus DIY or tailor brief. Then a two-box split: "AI proposes from approved recipes" and "Feasibility engine checks, in mm". Draw from the advisor deck concept slides, relabelled. | PLANNED / CONCEPT DIAGRAM | Advisor deck slides 1, 7 | G2, G3 |
| 1c | 2:45 to 3:15 | K | Coverage ladder (Level 1 woven shirt, Level 2 jersey tee conditional, Level 3 inspiration only) then the P0 to P4 phase bar with dates marked "internal, provisional". | PLANNED | Advisor deck slide 4; Blueprint section 12 (phase dates) | G4, G5 |
| 2a | 3:15 to 4:50 | K | Screen recording of the GitHub repo (private; record while signed in, hide tokens, no secrets in frame): folder tree, `.claude/agents/` list, the guard hooks folder, then the PR list showing the 14 merged on 1 Nov (about two minutes, one account), the 11 merged on 9 Nov (under five minutes, one account) and the open PRs. On-screen text: "29 agent definitions. Hooks block agent merge and approve commands. main requires a PR; no approval currently required. 14 PRs merged 1 Nov, 11 more 9 Nov." | RECORDED FROM REPO | commit `84efce5`; `.claude/agents/` (29 files); `.claude/hooks/` | R1, R2, R3 |
| 2a-slot | (within 2a) | K | SLOT-1: show the merged PR list with the as-of date on screen (contracts draft #15, API #22, cut guide #24 and result screens #25 merged). Open PRs (#23 model pipeline, #20, #21, #36, #44) shown as "open, not merged" and not narrated as done. | RECORDED FROM REPO | GitHub PR list, 9 Nov | R3 |
| 2b-i | 4:50 to 5:20 | N | Whiteboard or paper: hand-drawn shirt front, the 760 / 520 / 20 / 540 / 220 mm crop sum (deck slide 8: 76, 52, 2 cm, cut mark 54; same example as the interim report, marked illustrative) written out, with chalk marks. Tag: "ILLUSTRATIVE, NOT MEASURED". | ILLUSTRATIVE NUMBERS | Advisor deck slide 8 | P1, P2 |
| 2b-ii | 5:20 to 5:55 | N | THE REJECTION: a clean card showing the request ("add a peplum"), the engine's reason in plain words and mm ("strip needed 1,400 x 180 mm; offcut gives about 1,120 mm"), and the suggested alternative. Variant A (default now): redraw as an illustrative card tagged `ILLUSTRATIVE NUMBERS`. Variant B (replaces the peplum with the impossible-lengthening case, only if N1/N2 confirm that case exists and passes): terminal capture of the real test output tagged `RECORDED FROM REPO`. No peplum rule exists on main, so the peplum card stays illustrative. | A: ILLUSTRATIVE; B: RECORDED FROM REPO | A: Advisor deck slide 8; B: confirm with N1/N2 | P3 or R4 |
| 2b-iii | 5:55 to 6:15 | N | Pytest or benchmark summary. SLOT-2 default: a card reading "Engine and constraint suite merged (synthetic cases, not a measured shirt). Automated check on main passes at 9 Nov 2026 (27 cases, 29 checks)." Evidenced variant: a real run on main on recording day, with its own passed total (CI Benchmarks on main at 8b6faa5 reported 27 cases, 29 checks, synthetic inputs). | STATUS AS OF 9 Nov 2026 (default) / RECORDED FROM REPO (if real run) | #12, #9 merged; CI Benchmarks run on main (8b6faa5); #19 merged | R4 |
| 2c | 6:15 to 7:05 | D | Default (SLOT-6): screen recording of the merged intake screens (entry, capture, inspiration, measurements) on sample data, then the merged result cards and cut guide (diagram only, no overlay) on mock data, all tagged `PROTOTYPE, SAMPLE DATA`. Show the MOCK DATA badge in frame: the cards say "Verified within supported checks" beside it. Do not show the edit-then-cut path (it ends at a "could not find that version" screen) and do not claim intake leads into the studio. State how the capture was made (web, emulator or device); X1 reports no device run. | PROTOTYPE, SAMPLE DATA | `apps/mobile/app/(intake)/` (#14), result screens (#25), cut guide (#24) on `main`; X1 rechecks 9 Nov found no merge blockers (demo-only, mock data) | M1, M2, M3, M4 |
| 2c-slot | (within 2c) | D | SLOT-3: default card "Interviews and usability sessions: planned, consent forms in draft, not started". | PLANNED | none | G6 |
| 2d | 7:05 to 7:35 | N | Plain card, no animation: "Phase P0 (prove one measured transformation): rated RED in the L0 digest of 1 Nov 2026 (latest on main). 0 of 5 exit-evidence items fully met. No physical make recorded in the repository as of 9 Nov 2026." SLOT-4 swaps in founder-confirmed physical status. | STATUS AS OF 9 Nov 2026 | L0 baseline audit `docs/digests/2026-10-28-baseline-audit.md` (on `main`); L0 digest `docs/digests/2026-11-01.md` (merged, #26) | G7 |
| 3a | 7:35 to 8:00 | K | Architecture sketch (app, API, AI layer, feasibility engine, storage), each box tagged "proposed" or "planned". | PLANNED | Advisor deck slide 11 | G8 |
| 3b | 8:00 to 8:15 | N | Table of the evidence plan: 24 constraint scenarios (proposed), 4 DIY makes (proposed). Empty "Result" column visibly empty. | PLANNED / PROPOSED | Advisor deck slide 12 | G9 |
| 3c | 8:15 to 8:30 | D | Plan cards: 8 to 12 design participants, 2 to 3 tailors or makers (proposed targets). | PLANNED / PROPOSED | Advisor deck slide 12 | G9 |
| 4 | 8:30 to 9:30 | N, D, K | Three founders to camera or voice-over over the real shirt shot from scene 0. Last frame: team names, "Interim presentation, FYP 2026 S1", and the line "Targets are not results." | REAL FOOTAGE (planned) | none yet; line stating the P0 gate has not passed is per the L0 audit | A3, A4 |

## Variant plan

- **Variant A (default, if P0 physical trial is not done by recording day):** as above. Scene 2d and the conclusion state plainly that no measured result exists and that the P0 gate has not passed.
- **Variant P (if the physical trial is done and X2 has cleared the numbers):** replace scene 2b-i with real before and after shots of the shirt and a predicted-versus-measured table in mm with the number of measurements as the denominator. Keep the rejection scene. Edit narration lines tagged SLOT-2 and SLOT-4 only.

Do not mix: either every number on screen is from the cleared evidence log, or it carries `ILLUSTRATIVE` in frame.

## Accessibility and captions

- Burned-in captions on all narration (needs-human: final caption check). Contrast and text size readable at phone size.
- No information carried by colour alone; status badges show text.
- Captions file to be produced from the final narration (planned).

## Post-production notes (needs-human)

- Editor, tool, music (royalty-free only, licence recorded) and where raw footage is stored (outside the repo).
- No media files are committed to the repo. Only text planning docs live here.
