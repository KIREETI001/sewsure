# FYP interim video: storyboard (draft v0)

Status: DRAFT. Every visual below is **PLANNED** unless the Evidence column says a repo path or document that exists today. Nothing here has been filmed.

Runtime target 9:00. Narration is in `narration-script.md`; film list is in `shot-list.md`; claim IDs resolve in `../claims-register.md`.

## On-screen label rules (apply to every scene)

- Corner tag on every screen capture: `MOCK-UP`, `RECORDED FROM REPO`, `ILLUSTRATIVE NUMBERS`, `PLANNED` or `REAL FOOTAGE`. Use exactly one per shot, never none.
- Any number on screen carries a lower-third source line, for example: `Source: team survey, n = 25, directional only`.
- No body measurements of a real person on screen. Garment measurements are fine. Body-profile screens use sample values labelled `SAMPLE DATA`.
- No faces, no real user photos (non-negotiable 7). Team members appear only with their consent, recorded in the consent log (needs-human).

## Scenes

| # | Time | Speaker | Visual (what the viewer sees) | Label | Evidence today | Shot ID |
|---|---|---|---|---|---|---|
| 0 | 0:00 to 0:25 | D | Slow top-down shot of a real oversized woven shirt on a table, ruler and tailor's chalk beside it. Title card: "SewSure. FYP interim presentation. 10 Nov 2026." | REAL FOOTAGE (planned) | none yet | A1, A2 |
| 1a | 0:25 to 1:10 | D | Four large numbers appear one at a time: 24/25, 17/25, 21/25, 12/25, each with its plain-words caption. Footer on all: "Team exploratory survey, n = 25. Small, non-representative sample. Directional only." | REAL DATA (survey) | Scope V0.2 section 01; Advisor deck slide 2. Raw export not in repo (see register C-01) | G1 |
| 1b | 1:10 to 2:10 | K | Three-step graphic: photograph and measure, redesign options checked, cut guide plus DIY or tailor brief. Then a two-box split: "AI proposes from approved recipes" and "Feasibility engine checks, in mm". Draw from the advisor deck concept slides, relabelled. | PLANNED / CONCEPT DIAGRAM | Advisor deck slides 1, 7 | G2, G3 |
| 1c | 2:10 to 2:40 | K | Coverage ladder (Level 1 woven shirt, Level 2 jersey tee conditional, Level 3 inspiration only) then the P0 to P4 phase bar with dates marked "internal, provisional". | PLANNED | Advisor deck slides 4, 13; Blueprint section 12 | G4, G5 |
| 2a | 2:40 to 3:50 | K | Screen recording of the GitHub repo (private; record while signed in, hide tokens, no secrets in frame): folder tree, `.claude/agents/` list, the guard hooks folder, then the PR list showing agent branches awaiting review. Overlay: "29 agent definitions. Agents cannot merge." | RECORDED FROM REPO | commit `84efce5`; `.claude/agents/` (29 files); `.claude/hooks/` | R1, R2, R3 |
| 2a-slot | (within 2a) | K | SLOT-1: if the contracts PR is merged, show the merged PR title. Default: show the PR as "open, in review". | RECORDED FROM REPO | pending K1 | R3 |
| 2b-i | 3:50 to 4:20 | N | Whiteboard or paper: hand-drawn shirt front, the 780 / 500 / 30 / 530 / 250 mm crop sum written out, with chalk marks. Tag: "ILLUSTRATIVE, NOT MEASURED". | ILLUSTRATIVE NUMBERS | Blueprint section 5.3 | P1, P2 |
| 2b-ii | 4:20 to 5:00 | N | THE REJECTION: a clean card showing the request ("add a peplum"), the engine's reason in plain words and mm ("strip needed 1,400 x 180 mm; offcut gives about 1,120 mm"), and the suggested alternative. Variant A (default now): redraw as an illustrative card tagged `ILLUSTRATIVE NUMBERS`. Variant B (only if engine test exists): terminal capture of the real test output tagged `RECORDED FROM REPO`. | A: ILLUSTRATIVE; B: RECORDED FROM REPO | A: Advisor deck slide 8; B: pending N1/N2 | P3 or R4 |
| 2b-iii | 5:00 to 5:20 | N | Pytest or benchmark summary. SLOT-2 default: a card reading "Engine and first tests in progress. No pass count to report yet." Evidenced variant: real run, "x of y cases pass", denominators in frame. | PLANNED (default) / RECORDED (if real) | pending N1/N2 | R4 |
| 2c | 5:20 to 6:20 | D | Four phone-frame screens from the mocks: capture, measurement guide (SAMPLE DATA), result card showing a status badge and fewer than three options, cut guide with a "check with your ruler" step. Large permanent `MOCK-UP` watermark. | MOCK-UP | pending D1 to D5 designs; Figma frames if they exist | M1 to M4 |
| 2c-slot | (within 2c) | D | SLOT-3: default card "Interviews and usability sessions: planned, consent forms in draft, not started". | PLANNED | none | G6 |
| 2d | 6:20 to 6:40 | N | Plain card, no animation: "Phase P0 (prove one measured transformation): rated red. No physical trial result yet." SLOT-4 swaps in if evidence arrives. | REAL STATUS | L0 status (source: lead brief; re-verify against L0 weekly report before recording) | G7 |
| 3a | 6:40 to 7:10 | K | Architecture sketch (app, API, AI layer, feasibility engine, storage), each box tagged "proposed" or "planned". | PLANNED | Advisor deck slide 11 | G8 |
| 3b | 7:10 to 7:40 | N | Table of the evidence plan: 24 constraint scenarios (proposed), 4 DIY makes (proposed). Empty "Result" column visibly empty. | PLANNED / PROPOSED | Advisor deck slide 12 | G9 |
| 3c | 7:40 to 8:00 | D | Plan cards: 8 to 12 design participants, 2 to 3 tailors (proposed targets). | PLANNED / PROPOSED | Advisor deck slide 12 | G9 |
| 4 | 8:00 to 9:00 | N, D, K | Three founders to camera or voice-over over the real shirt shot from scene 0. Last frame: team names, "Interim presentation, FYP 2026 S1", and the line "Targets are not results." | REAL FOOTAGE (planned) | none yet | A3, A4 |

## Variant plan

- **Variant A (default, if P0 physical trial is not done by recording day):** as above. Scene 2d and the conclusion state plainly that no measured result exists.
- **Variant B (if the physical trial is done and X2 has cleared the numbers):** replace scene 2b-i with real before and after shots of the shirt and a predicted-versus-measured table in mm with the number of measurements as the denominator. Keep the rejection scene. Edit narration lines tagged SLOT-2 and SLOT-4 only.

Do not mix: either every number on screen is from the cleared evidence log, or it carries `ILLUSTRATIVE` in frame.

## Accessibility and captions

- Burned-in captions on all narration (needs-human: final caption check). Contrast and text size readable at phone size.
- No information carried by colour alone; status badges show text.
- Captions file to be produced from the final narration (planned).

## Post-production notes (needs-human)

- Editor, tool, music (royalty-free only, licence recorded) and where raw footage is stored (outside the repo).
- No media files are committed to the repo. Only text planning docs live here.
