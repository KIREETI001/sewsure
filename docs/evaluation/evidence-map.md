# Evidence map

Each claim the team plans to make in the FYP report (interim due 10 Nov 2026) or the pitch, the evidence that would support it, and its status today.

**Status as of 1 Nov 2026: no physical make, no benchmark run, no pilot and no usability session has been reported to this evidence base.** "No data yet" means exactly that. Nothing here is a result. Sources for the planned metrics are the Technical Implementation Blueprint V0.1 (§6.3, §12, §17.2 to §17.4, §18.3) and the repo `CLAUDE.md` rules (denominators; no guarantee language).

Status values: `no data yet`, `draft only` (an artefact exists but has not been reviewed or run), `partial` (some data, stated), `supported` (data committed with denominator). Update this file only from committed data. Do not change a status on someone's say-so.

Wording rule: until a row is `supported`, the report and pitch may say the item is **planned** or **proposed**. They may not say it works. Banned words: guaranteed, perfect fit, precision AR, 100% accurate.

## Claims

| # | Planned claim (wording must stay within the evidence) | Evidence that would support it | Where it comes from | Status |
|---|---|---|---|---|
| C1 | One real woven shirt was measured, marked, cut and hemmed from a dimensioned cut plan, and the deviation was recorded (P0 gate). | A completed `physical-make-record` with real rows, ruler check by a person, photos with consent. Figures from `make_report.py`. | Blueprint §12 P0; this kit | no data yet |
| C2 | Predicted cut marks differed from independent ruler readings by X mm (median) and Y mm (maximum), over n makes and k marks. | `make_report.py` output from real rows; sample size stated; tolerance agreed with the sewist **before** the run. | §6.3, §17.4 | no data yet |
| C3 | Finished-garment length differed from the planned length by X mm, with reasons for any rework. | Same record, `finished_length_*` rows, `error_cause`, `rework_reason`. | §17.3, §17.4 | no data yet |
| C4 | The crop recipe was reviewed by a sewist. | Named reviewer and date in `recipe.yaml` (`status: reviewed`), written sign-off. | Blueprint §18.3 G1; task H-02 | draft only (PR #11, `reviewed_by: null`) |
| C5 | The feasibility engine rejects impossible designs (e.g. lengthening, no positive remainder, hem allowance overlapping buttons). | The 24-case constraint suite run in CI: correct rejection, false acceptance, false rejection, indeterminate, each as numerator/denominator. | §17.2, §17.4 | no data yet (the 24-case set is a proposal, not a sample-size justification) |
| C6 | False feasible approval rate on the test set is a/b. | Same suite; any false approval on a destructive cut is investigated. | §17.2, §17.4 | no data yet |
| C7 | The AI model only picks allow-listed recipes and never invents pattern geometry. | JSON parse rate and recipe-ID validity from the AI eval set, as numerator/denominator, plus the schema that rejects numeric geometry. | §4, §17.4 | no data yet (design rule in `CLAUDE.md`; not measured) |
| C8 | The AI selected the supported recipe in a/b human-labelled requests. | Labelled request set and agreement count. | §17.4 | no data yet |
| C9 | Calibrated photo overlay error was X mm median, Y mm worst case under stated conditions, with rejection reasons. | Overlay QA trials: photo with ruler, independently measured reference points, displayed vs actual positions. | §6.3, §17.4 | no data yet |
| C10 | Users completed k of n tasks unaided; median time; clarifying questions; self-reported confidence. | De-identified usability sessions (participant codes), consent on file. | §17.4 | no data yet |
| C11 | Tailor briefs were understood without correction in a/b cases; real quotes received. | Tailor sessions with team-created tests; counts. | §17.4, §10.3 | no data yet |
| C12 | Cost per successful checked design was X, with retry/failure percentage. | Application Insights cost trace, definition of "successful checked design". | §17.4 | no data yet |
| C13 | An unverified image never reaches a "safe to cut" screen; previews are labelled approximate. | Screens and state-machine tests showing the cut screen is reachable only for `PASS_SUPPORTED_CHECKS` with a verified view. This is a design property, shown by tests, not a statistic. | `CLAUDE.md` rule 5, §18.3 G2 | no data yet |
| C14 | Revisions are immutable and any edit invalidates downstream cut plans/DIY steps/briefs. | Contract tests and fixtures in `packages/contracts`. | `CLAUDE.md` rule 3 | draft only (contract v1 is a draft, PR #15) |
| C15 | Measurements are stored in mm with origin and `confirmed_at`. | Schema + tests. | `CLAUDE.md` rule 1 | draft only |
| C16 | Demand: x people joined the waitlist / y of z interviewed makers said ... | Waitlist export counts and de-identified interview notes with denominators. | Product scope; research | no data yet |
| C17 | Sustainability/need statements (e.g. how many garments unused). | A cited external source with a date, or the team's own survey with n. Otherwise do not state a number. | docs rule: every number needs a source | no data yet |
| C18 | Four physical makes in total were completed (proposed target). | Four records. | Blueprint §12 P3 (proposed) | no data yet (0 of a proposed 4) |

## What the interim report (10 Nov) can honestly say today

Only: the approach and design (planned), the draft recipe and the P0 make procedure exist, and which evidence is still to be collected. If the P0 make is done before the deadline, it supports C1 to C3 with n = 1 make, stated as such, and nothing about typical performance.

## needs-human

- Run the P0 make and fill in the record (see `p0-make-kit.md`).
- Sewist sign-off of the recipe (C4).
- Agree tolerances with the sewist before results are seen (C2, C9).
- Decide which claims go into the interim report and the pitch; X2 audits them before they leave the team.
- Consent, recruiting participants and tailors (C10, C11); outreach and waitlist exports (C16).
- Provide a cited source for any need or market statistic (C17).
