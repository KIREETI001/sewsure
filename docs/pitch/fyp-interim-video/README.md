# FYP interim video presentation

Owner: D8 Pitch & Demo Producer. Human approver: Delfine (A3: all three founders). X2 must clear every claim before recording.

Due **10 Nov 2026**, submitted to the supervisor and examiner with the interim report (source: `fyp deadlines.pdf`, FYP 2026 S1 row). X3 drafts the interim report in `docs/reports/`; keep both documents on the same facts, and use the claims register as the shared fact list.

## Files

| File | Purpose |
|---|---|
| `narration-script.md` | Timed narration, split by founder, with claim IDs and evidence slots |
| `storyboard.md` | Scene table: visual, label, evidence, shot IDs |
| `shot-list.md` | What to film or capture, owner, consent, needs-human |
| `../claims-register.md` | Every claim, source, status |

## Structure (matches NTU suggested interim report format)

1. Introduction and objectives: 0:25 to 3:15
2. Work done so far: 3:15 to 7:35
3. Future work: 7:35 to 8:30
4. Honest conclusion: 8:30 to 9:30

## Where the project stands when this was drafted (28 Oct 2026)

- Facts below were updated on 9 Nov 2026 (`main` at 8b6faa5); the on-screen as-of date is set to 9 Nov 2026 and Kireeti can change it; every spoken status needs an on-screen "as of [date]" and a re-check on recording day.
- Evidenced: planning documents (Scope V0.2, Blueprint V0.1, advisor deck of 22 Oct 2026), the n = 25 survey as reported in those documents, a repo scaffold with 29 agent definitions and guard hooks, fourteen PRs merged on 1 Nov 2026 in about two minutes and eleven more on 9 Nov in under five (#19, #34, #17, #18, #26, #35, #22, #24, #25, #40, #41), all from the `KIREETI001` account with no approving review. Now on `main`: first engine, constraint suite (27 cases, 29 checks, synthetic; CI Benchmarks passes on `main`), contract draft.3 with `REVISION_STALE`, an API that calls the engine, intake screens, result cards and a cut guide as demo-only screens on mock data (X1 9 Nov rechecks: no merge blockers). Open: #23 (model pipeline), #20, #21, #36, #44 and others.
- Still true: dimensioned diagram only, no overlay; AI pipeline not connected to the API; no device or live-model run recorded; recipe is a draft; intake does not link to the Design Studio and the edit-then-cut demo path dead-ends.
- Not evidenced: any measured shirt, a verified test result, any live Azure call, any usability session, any tailor quote.
- Phase P0 is rated RED in L0's audit (baseline audit and 1 Nov digest, both on `main`; no later digest). The script therefore defaults to the honest "not yet" wording, with explicit evidence slots to swap in if real results land before recording.

## Pre-record checklist (the SLOTs)

| Slot | Default wording stays unless | Evidence needed | Who checks |
|---|---|---|---|
| SLOT-1 merged work | state re-read on recording day | PR list with as-of date on screen | Kireeti |
| SLOT-2 engine and tests | main green on recording day (CI Benchmarks passed on `main` at 8b6faa5), suite run | test output with real passed/total (27 cases, 29 checks in the CI run on `main`) | Narthananilaa, X2 |
| SLOT-3 research | D7 sessions actually held, consented | de-identified notes, counts with denominators | Delfine, X2 |
| SLOT-4 P0 physical trial | measured shirt made and recorded | physical record: predicted and measured mm, number of measurements | Narthananilaa, X2 |
| SLOT-5 conclusion | any of the above change | as above | all three |
| SLOT-6 app screens | D3/D4 PRs (#25, #24) merged (done 9 Nov) | merged PR per screen | Delfine, X2 |

## Open questions for the founders

1. NTU video length and format limit: not stated in the source PDFs. Draft assumes 8 to 10 minutes as instructed.
2. Is the shirt for the P0 trial chosen? Whose is it, and do they consent to appear?
3. Who speaks which section: draft follows the ownership table in `CLAUDE.md`; swap if preferred.
4. Do you want a live demo clip? Draft uses the merged intake screens on sample data (tagged `PROTOTYPE, SAMPLE DATA`) and labelled mock-ups, because no connected build is evidenced.
5. Status date is 9 Nov 2026 in both this script and #8; the founders can change it.
6. Peplum example: the deck lists a peplum as "later, needs proof", so a real rejection of a peplum by the engine may not be possible by 10 Nov. See rejection scene variants in `storyboard.md` and ask Narthananilaa whether N1/N2 will have a material-check rejection test by then (the blueprint's mandatory smoke test already includes an impossible lengthening request, which is the safer real alternative).

## needs-human

- Film real footage; record narration; decide on-camera people (shot-list A1 to A5).
- Confirm NTU length limit and format.
- File the NTU generative AI declaration covering the agent workflow shown in the video.
- Final caption review; music or font licences.
- Approve the script (A3: all three founders).
- Confirm any physical make done off the repository (SLOT-4), with date and what was measured.
- Agree one evidence-freeze date with X3 and L0; decide whether to close the shared-account merge route (L0 decision P-03).
