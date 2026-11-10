# FYP interim video presentation (3:00 summary)

Owner: D8 Pitch & Demo Producer. Human approver: Delfine (A3: all three founders). X2 must clear every claim before recording.

Due **10 Nov 2026**, submitted to the supervisor and examiner with the interim report (source: `fyp deadlines.pdf`, FYP 2026 S1 row). Maximum length 3:00, confirmed by Kireeti (the NTU PDFs state no limit). X3 drafts the interim report in `docs/reports/`; keep both documents on the same facts, and use the claims register as the shared fact list. The earlier 10-minute version is in git history (commit `331ffe5`).

## Files

| File | Purpose |
|---|---|
| `narration-script.md` | Timed narration, split by founder, with claim IDs, word count and time estimate |
| `storyboard.md` | Scene table: visual, label, evidence, shot IDs |
| `shot-list.md` | What to film or capture, owner, consent, needs-human |
| `../claims-register.md` | Every claim, source, status |

## Structure (matches the NTU interim format)

1. Introduction (problem, survey, what SewSure is): 0:00 to 0:59
2. Work done so far (engine, API, demo screens): 0:59 to 1:26
3. Not done, and how we use agents: 1:27 to 2:26
4. Future work and conclusion: 2:26 to 2:47

Estimated running time about 2:51 (about 2:54 if numbers are said in full); 377 spoken words (Delfine 117, Kireeti 174, Narthananilaa 80, all 6) at an assumed 140 wpm. See Totals in `narration-script.md`.

## Where the project stands (9 Nov 2026, `main` at 8b6faa5)

- Evidenced: engine and 27-case synthetic suite with all 29 checks matching in CI on `main`; API calls the engine (#22); demo screens on mock data (intake #14, result cards #25, cut guide #24; X1 found no merge blockers); 29 agent definitions and guard hooks; 14 PRs merged on 1 Nov and 11 on 9 Nov.
- Not done: no physical make; shirt not chosen; no sewist review (recipe is a draft); P0 rated RED (1 Nov digest); no overlay; AI pipeline not connected to the API (#23 open); Azure not set up; no phone run recorded; no interviews.
- Supplied by founders through the lead session, not opened by D8: survey sample description (C-40), Samsung S24 Ultra with Expo build service (C-42), "I ran all 25 merges after approving each batch" (C-44).

## Pre-record checklist

| Check | Needed | Who |
|---|---|---|
| CI on `main` still green; merged list unchanged | re-read on recording day, as-of date on screen | Kireeti |
| S4b device and build-service wording | confirm or cut the clause | Kireeti, Delfine |
| S5 merge sentence | confirm | Kireeti |
| Running time | stopwatch read-through, under 3:00 | all three |
| M3 recording | MOCK DATA badge in frame; say "Verified is sample text"; do not film edit-then-cut | Delfine |

There are no slot variants for a physical make: none has happened. If one happens before recording, add a new register row and get X2 to clear it first.

## Open questions

1. NTU video length: 3:00 maximum per Kireeti; not stated in the source PDFs.
2. Status date is 9 Nov 2026 in both this script and #8; the founders can change it.
3. Who speaks which section: split by the ownership table in `CLAUDE.md`; swap if preferred.

## needs-human

- Film real footage; record narration; decide on-camera people (shot-list A1, A3).
- Confirm NTU length limit and format.
- File the NTU generative AI declaration covering the agent workflow shown in the video.
- Final caption review; music or font licences.
- Approve the script (A3: all three founders).
- Confirm the founder-supplied facts listed above.
