# Claims register (draft v0)

Owner: D8 Pitch & Demo Producer. Auditor: X2 Claims & Integrity Auditor (to audit later). Written 28 Oct 2026.

Covers the FYP interim video (`fyp-interim-video/`) and the Imagine Cup pitch outline (`imagine-cup/pitch-outline-v0.md`). Add a row before any new claim is used in either.

## Status vocabulary

- **evidenced**: a source exists today that X2 can open (a repo path, a source PDF section, a log). Read the Notes column for limits.
- **planned**: describes intended or proposed work, or illustrative numbers. Must be spoken and shown as planned or illustrative. It is not a result.
- **needs data**: a result-type claim with no evidence yet. Must not appear in any output until data exists and X2 clears it.

X2 verdict column is empty on purpose.

## Source key

| Key | Document |
|---|---|
| SCOPE | `SewSure_Source_of_Truth_Product_Scope_V0.2.pdf`, 22 Oct 2026 |
| BP | `SewSure_Technical_Implementation_and_3_Person_Plan_V0.1 (1).pdf` (blueprint), 22 Oct 2026 |
| DECK | `SewSure_Advisor_Presentation.pdf`, 14 slides, 22 Oct 2026 |
| DL | `fyp deadlines.pdf`, captured 22 Oct 2026 |
| FMT | `SuggestedFormatInterimReport.pdf` |
| REPO | this repository, commit `84efce5` and later |
| L0 | lead agent brief for this task (P0 rated red) |

Source PDFs live in the parent folder outside the repo.

## Register

| ID | Claim (as said or shown) | Used in | Source | Status | Denominator / limits | Evidence still needed | X2 |
|---|---|---|---|---|---|---|---|
| C-01 | 24 of 25 survey respondents had no sewing experience or were beginners | Video S1a; IC criteria (inclusive design) | SCOPE section 01; DECK slide 2 | evidenced | n = 25, small non-representative sample, directional only | Raw survey export filed under `docs/research/` (D7) so figures can be re-derived. Currently only secondary reports exist | |
| C-02 | 17 of 25 had rejected second-hand clothing because of fit | Video S1a | SCOPE section 01; DECK slide 2 | evidenced | n = 25, directional only | same as C-01 | |
| C-03 | 21 of 25 rated the proposed tool 4 or 5 for usefulness | Video S1a | SCOPE section 01; DECK slide 2 | evidenced | n = 25; rated a description of a proposed tool, not a built product; does not show willingness to pay or technical accuracy (SCOPE section 01) | same as C-01 | |
| C-04 | 12 of 25 would consider finding a tailor through the app | Video S1a | SCOPE section 01 | evidenced | n = 25; "in the stated scenario" | same as C-01 | |
| C-05 | SewSure's intended flow: photograph a garment, state intent, confirm measurements, up to three redesigns that passed the implemented checks, then a cut guide plus DIY steps or a tailor brief | Video S1b; IC idea | SCOPE section 01 and 05; DECK slide 1 | planned | Describes the intended product. Wording must stay "aims to" / "intended" | Working end-to-end build | |
| C-06 | Project objectives: prove one measured transformation; connect it into a prototype; report passes, failures and mistakes with denominators | Video S1b | BP sections 11-12, 17; DECK slides 13-14 | planned | These are objectives, not outcomes | none for the objective itself | |
| C-07 | Design principle: AI may only choose recipe IDs and parameters from an allow-list; a deterministic engine checks the numbers and alone sets design status | Video S1b; IC cloud and AI | Root `CLAUDE.md` non-negotiables 2 and 4; DECK slide 7; BP section 4 | evidenced (as a documented rule); implementation planned | The rule is documented. Its enforcement in code is not yet evidenced (see C-08) | Merged engine and API code plus a trace | |
| C-08 | The feasibility engine works and passes its tests | Video S2b (SLOT-2); IC | none today | needs data | Report passed/total, e.g. "x of 24 cases" (24 is a proposed count, C-17) | N1/N2 merged PRs and test output; false approvals, false rejections, indeterminate counts | |
| C-09 | The repository is a monorepo with app, API, feasibility, contracts, recipes and benchmarks folders, 29 agent definitions, and guard hooks that block edits to secrets and production infrastructure | Video S2a | REPO: `.claude/agents/` (29 files), `.claude/hooks/`, commit `84efce5`; root `CLAUDE.md` | evidenced | Scaffold and definitions only. Does not mean the code inside exists | Re-count agents at recording time | |
| C-10 | Agents work in branches and open pull requests; they cannot merge; a human code owner approves each change on a protected `main` | Video S2a | Root `CLAUDE.md` "How agents work here"; L0 brief (branch protection) | evidenced | Process rule as documented. Branch protection setting was stated in the L0 brief, not independently seen by D8 | Screenshot of branch protection rule (Kireeti) | |
| C-11 | Written project rules: lengths in mm, design status set only by the engine, immutable revisions, no guarantee language, contract-first | Video S2a | Root `CLAUDE.md` non-negotiables 1, 2, 3, 6, 9 | evidenced | Rules written, enforcement partly planned | none for the rule itself | |
| C-12 | Scope: Level 1 oversized woven button-up shirts verified flagship; Level 2 jersey tee limited and conditional; everything else inspiration only with no cut plan | Video S1c; IC limits | SCOPE section 03; DECK slide 4 | evidenced (as scope decision) | Support levels are scope, not proven capability. Tee and accessory items conditional | none for the scope statement | |
| C-13 | Illustrative crop sum: original length 780 mm, finished 500 mm, hem 30 mm, cut mark 530 mm, removed 250 mm | Video S2b; IC moment 1 (illustrative only) | BP section 5.3. DECK slide 8 uses a different illustrative example (76 / 54 cm) | planned (illustrative) | **Not measured.** Two illustrative sets exist and differ; use one and always tag ILLUSTRATIVE | Replace with real measurements before any "result" use | |
| C-14 | Peplum example: needs a 140 x 18 cm strip, offcut yields about 112 cm, so rejected with a shorter or less full alternative | Video S2b; IC moment 2 | DECK slide 8 | planned (illustrative) | Illustrative numbers. Peplum is listed as later, needs proof (DECK slide 4). Whether an implemented peplum rule exists is unknown | A real test case that produces this rejection, or swap to the impossible-lengthening case (BP 5.5, 15.3) | |
| C-15 | Predicted versus ruler-measured dimensions for a real shirt, with absolute errors in mm | IC moment 1; Video variant B | none today | needs data | State number of garments and measurements as denominator; one shirt is one case | Physical validation record (BP 17.3): measured shirt, mark, sew, measure. Depends on P0 gate | |
| C-16 | Phase P0 (prove one measured transformation) is rated red | Video S2d | L0 brief; BP section 12 (P0 pass criterion) | evidenced | Status as of 28 Oct 2026. Will change | Re-check against L0 weekly report before recording | |
| C-17 | 24 constraint scenarios are proposed (6 successful, 6 insufficient fabric or invalid panel, 4 missing or implausible measurements, 4 unsupported, 4 revision or edge cases) | Video S3b | BP section 17.2; DECK slide 12 | planned | Proposed suite, not a sample-size justification and not results. Do not say "we test 24 cases" until it exists | Merged benchmark suite and run | |
| C-18 | Proposed targets: 4 DIY makes; 8 to 12 design participants; 2 to 3 makers | Video S3b, S3c | DECK slide 12; BP section 20 (D12) | planned | Proposed targets, numeric thresholds not agreed (SCOPE section 12) | Recruitment and consent records | |
| C-19 | A tailor quoted from a SewSure brief | IC moment 3; Video S3c | none today | needs data | Quotes may initially come from team-created test accounts (BP risk register). Must be disclosed | Consented tailor session, de-identified (T01), time to quote, clarification count | |
| C-20 | App screens shown are mock-ups, not the connected product | Video S2c | Design plan; DECK slides 6, 9 (conceptual UI) | planned | Always watermark MOCK-UP | D1 to D5 designs; a real connected build for any non-mock claim | |
| C-21 | Azure AI Foundry / Azure OpenAI as the model layer; live access verified | IC cloud and AI; Video S3a | DECK slide 11 ("proposed"); BP section 11.2, P0 task "verify live Azure access" | planned | Azure choices provisional. No evidence of live access yet | Real structured response, request trace, date and deployment ID (K3) | |
| C-22 | Imagine Cup 2027 eligibility, rules, deadline and criteria are unconfirmed | Video S4; IC outline | BP section 12 historical targets note; DECK slide 11 footer; BP references C1 to C3 | evidenced (that it is unconfirmed) | The 2025-26 criteria in the outline come from the D8 task brief, not a primary source D8 opened | Official portal check (Kireeti) | |
| C-23 | Phase windows P0 22 Oct-1 Nov, P1 2-15 Nov, P2 16 Nov-6 Dec, P3 7-22 Dec, P4 23 Dec-7 Jan; internal and provisional | Video S1c | DECK slide 13; BP section 12 | planned | Internal proposals, not official competition dates | none | |
| C-24 | No in-app payment in the initial MVP | IC viability | SCOPE section 09; DECK slide 10 | evidenced (scope decision) | Scope statement | none | |
| C-25 | Previews are approximate (2D silhouette plus numeric fit, no drape); an unverified design never reaches a safe-to-cut screen | Video S2c | SCOPE section 07; root `CLAUDE.md` non-negotiable 5 | evidenced (as rule) | Rule documented; UI enforcement planned | UI test or screenshot showing the rule held (D6) | |
| C-26 | Cost per successful checked design | IC cloud and viability | BP sections 11.5, 17.4 | needs data | Report numerator and denominator (cost over successful checked designs) and retry percentage | K7 cost trace | |
| C-27 | Work is split by area: Kireeti platform/backend/AI; Narthananilaa garment rules/feasibility/evidence; Delfine mobile/UX/research | Video speaker split | Root `CLAUDE.md` owner table; DECK slide 14 | evidenced | DECK calls the split "proposed, to be confirmed"; root `CLAUDE.md` lists it as the ownership table | Founders confirm | |
| C-28 | AI coding-agent assistance is declared on the NTU generative AI declaration form | Video S2a | `docs/CLAUDE.md`; DL (GAI declare form link) | needs data | A declaration obligation exists; the video says "will declare". Whether the form is filed is unknown | Filed form (needs-human) | |
| C-29 | Inclusive design: accessible labels, contrast, no colour-only status, beginner support | IC criteria | BP 17.1 (screen-reader labels), SCOPE section 08 (practice, checkpoints) | planned | Intended. No accessibility test exists | D6 accessibility results with counts | |
| C-30 | Business model: freemium is a hypothesis; commission is a later possibility, not assumed | IC viability | SCOPE section 09 | evidenced (as hypothesis) | The survey does not show willingness to pay (SCOPE section 01) | Willingness-to-pay evidence if wanted | |
| C-31 | Founder-led validation: sessions with beginners and a maker pilot | IC criteria | BP 17.1; DECK slide 12 | needs data | Only the n = 25 survey exists today | De-identified session notes with denominators (D7) | |
| C-32 | A recorded fallback demo exists and is labelled "recorded" | IC demo plan | BP 18.2 step 7, 20.2 | planned | Not yet produced | The recording | |
| C-33 | The video follows the NTU suggested interim format (Introduction; Work done so far; Future work; Conclusion) | Video structure | FMT; DL | evidenced | Format is a suggestion; length limit not stated in sources | Confirm limit with supervisor | |
| C-34 | One working model endpoint plus ordinary Azure hosting may not satisfy a requirement for multiple distinct Microsoft AI services; a second service must be load-bearing | IC cloud and AI | BP section 11.3 | evidenced (as a caution) | Depends on the final 2027 rules | Rules check; justify any second service by need | |

## Claims we will not make (and why)

| Do not say | Why |
|---|---|
| "Guaranteed fit", "perfect fit", "precision AR", "100% accurate", "safe to cut" for an unchecked design | Root `CLAUDE.md` non-negotiables 5 and 6 |
| Market size, revenue, user counts, retention, "users love it" | No source in the evidence set |
| That SewSure beats or replaces other tools | DECK slide 3 notes are preliminary team observations, not verified; a dash is not a claim of absence |
| That the survey proves demand or willingness to pay | SCOPE section 01 says it does not |
| That the model designs or draws patterns | Model only picks allow-listed recipe IDs and parameters |
| That tees, other garments or accessories are verified | Conditional or inspiration only (SCOPE section 03) |
| That 15 Nov, 15 Dec, 22 Dec or 7 Jan are official dates | Internal proposals (BP section 12) |
| "Three options" as a constant | The app never assumes exactly three exist (non-negotiable 8) |

## Hand-off to X2

- Resolve every `needs data` row before it appears in a final cut or deck. They are currently not used as facts anywhere in the draft script (default wording is the "not yet" version).
- Check each SLOT swap in `fyp-interim-video/narration-script.md` against the evidence listed here.
- Check the survey figures against the raw export when D7 files it.
