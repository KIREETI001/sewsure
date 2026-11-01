# Imagine Cup pitch outline v0

Status: DRAFT outline. Not cleared by X2. Written 28 Oct 2026.

> **TODO (blocking before this outline is used):** re-map to the official **Imagine Cup 2027** rules, judging criteria, weights, eligibility and deadlines once confirmed. The four criteria below are the 2025-26 criteria as given in the D8 task brief (Microsoft cloud and AI implementation, inclusive design, viability, founder-led validation). D8 has not independently verified their wording or weights; the Blueprint also says 2027 requirements are unverified and may differ (Blueprint section 11.3 and references C1 to C3; advisor deck slide 11 footer). Owner of the check: Kireeti, with Delfine. Do not submit or rehearse against a time limit until confirmed.

Time limit: unknown. For rehearsal drafts only, this outline assumes a **proposed 5-minute** live pitch. This is a working assumption, not a rule.

## One-line pitch (proposed)

"SewSure helps people turn a garment they already own into a redesign they can actually make, by letting AI propose and a deterministic feasibility check decide, and showing where it says no."

No guarantee language. No market size claim (none sourced).

## Criteria map

| Criterion (2025-26, unverified) | What we would show | Evidence needed | Status today | Claim IDs |
|---|---|---|---|---|
| **Microsoft cloud and AI implementation** | A model on Azure (Foundry / Azure OpenAI proposed) proposes a design from an allow-list of recipes under a JSON schema; the feasibility engine validates; the trace shows what the model did and what the engine decided. Honest account of what each Microsoft service does. | Verified live Azure access; a real structured response and trace; cost per checked design; the second service, if the rules require two, justified by real need (Blueprint 11.3: do not add Speech just to inflate a count). | planned. Azure choices provisional. Live access not yet evidenced. | C-07, C-21, C-26, C-34 |
| **Inclusive design** | Beginners with no sewing experience and low confidence are the target user; ruler checkpoints and practice steps before irreversible cuts; clear failure messages; accessible UI (labels, contrast, no colour-only status). | Accessibility checks (screen-reader labels, contrast), usability sessions including beginners, with denominators. Survey: 24/25 no or beginner sewing experience (directional). | planned. Survey only. No accessibility test yet. | C-01, C-29 |
| **Viability** | Honest path: freemium is a hypothesis; tailor handoff is secondary; no payments in MVP; cost per design under a budget cap; named limits (one garment family verified). | Cost per successful checked design; tailor willingness evidence; any willingness-to-pay evidence (none exists: the Scope says the survey does not show it). | planned. Business model is a hypothesis. | C-24, C-26, C-30 |
| **Founder-led validation** | Planned: the founders measure a real shirt, mark and cut it, sew it and compare predicted with measured mm; run sessions with beginners; and ask a tailor to quote from a SewSure brief. Each is a result only after it happens. | Physical make record; session notes (de-identified); tailor quote on a real brief with consent. | needs data. Survey n = 25 exists; nothing else yet. | C-15, C-19, C-31 |

Rule for every scoring claim in the final deck: a number appears only if it is in the claims register as **evidenced** with a source and denominator.

## Narrative arc (proposed, timings are placeholders until the limit is known)

| Part | Share | Content | Presenter (proposal) |
|---|---|---|---|
| 1 Hook | ~10% | The shirt in the wardrobe. The gap between an idea and making it. | Delfine |
| 2 Problem and evidence | ~10% | Survey n = 25, directional only; what it does and does not show. | Delfine |
| 3 Idea | ~10% | The three-step journey; AI proposes, engine checks, up to three options; it may show fewer or none. | Kireeti |
| 4 Stage moment 1: before and after | ~20% | Real garment, predicted vs measured mm. | Narthananilaa |
| 5 Stage moment 2: honest rejection | ~15% | The impossible peplum and why. | Narthananilaa |
| 6 Stage moment 3: tailor quote | ~15% | A tailor quotes from a SewSure brief. | Delfine + Kireeti |
| 7 How it is built | ~10% | Azure and architecture, trace, cost. | Kireeti |
| 8 Limits and what is next | ~10% | One garment family verified; failures we have; plan. | all |

## Stage moments (the three we plan to build the pitch around)

All three are **planned**. None exists today. If the evidence does not exist by pitch date, the moment is cut or shown as a clearly labelled illustration, never presented as a result.

### Moment 1: before and after garment, predicted vs measured mm

- Show: the real shirt before, the cut plan with marks, the sewn garment after, and a table of predicted vs ruler-measured dimensions.
- Table to fill from the physical record (blank until measured; do not pre-fill):

| Dimension | Predicted (mm) | Measured (mm) | Absolute error (mm) |
|---|---|---|---|
| Finished length | TO BE MEASURED | TO BE MEASURED | TO BE MEASURED |
| Cut mark from shoulder | TO BE MEASURED | TO BE MEASURED | TO BE MEASURED |
| Hem allowance | TO BE MEASURED | TO BE MEASURED | TO BE MEASURED |

- The 76 / 52 / 2 cm crop example (deck slide 8; 760 / 520 / 20 / 540 / 220 mm; the same example the interim report uses) is **illustrative only**. The blueprint 5.3 example (780 / 500 / 30 / 530 / 250 mm) is also illustrative. Never show it as a measurement.
- Report the number of garments and measurements as the denominator. One shirt is one case, say so. Include any mismatch and its cause.
- Evidence needed: physical validation record (Blueprint 17.3 template), consent for photos. Owner: Narthananilaa. Status: needs data. Depends on P0 pass (currently red).

### Moment 2: honest rejection of an impossible peplum

- Show: user asks for a peplum; the engine says no and why in mm (deck example: needs a 140 x 18 cm strip, offcut yields about 112 cm), and suggests a shorter or less full option; the app never produces a cut plan for it.
- Caveat: the advisor deck lists a peplum under "later, needs proof" (slide 4), and the numbers on slide 8 are illustrative. For a real on-stage rejection, the engine needs an implemented material check for that case. Safer real alternative already in the Blueprint smoke test: an impossible lengthening request (longer finished length than the available length with no extra fabric; Blueprint 5.5, 15.3 step 2).
- Evidence needed: a passing test case in the benchmark suite (N2) and a recorded trace. Owner: Narthananilaa, with Kireeti for the trace. Status: planned.
- This moment would be the strongest honesty signal for the "Microsoft AI plus deterministic check" story: the aim is to show the model proposing it and the engine refusing it (planned; not yet demonstrated).

### Moment 3: a tailor quoting from a SewSure brief

- Show: the auto-compiled brief (photos, consented measurements, selected design and its status, assumptions), a real tailor reading it, and a quote returned in the app (no payment).
- Evidence needed: a real tailor (needs-human), their recorded consent to appear, de-identified code (T01), time to quote, whether they needed to ask for clarification (the Blueprint plans to log this), the brief version they saw. Status: needs data. The Blueprint's risk register notes quotes may initially come only from team-created test accounts; if so, say "test quote from a tailor we recruited", never imply marketplace traction.
- Owners: Delfine (recruit and sessions, D7/D9), Kireeti (brief and quote flow, K8).

## Demo and fallback plan

- Primary: a short narrated recorded demo of the real shirt through the app, with live service optional.
- Fallback: a clearly labelled recorded trace after a live service failure (Blueprint 18.2 step 7). Label "recorded".
- Mock output is always labelled. Previews are labelled approximate.
- Rehearsal: timed once the limit is confirmed (D8 done criterion: the timed script fits the limit once confirmed).

## What we will not say on stage

- "Guaranteed fit", "perfect fit", "precision AR", "100% accurate", "safe to cut" for an unchecked design.
- Market size, revenue, user counts, or "users love it" (none evidenced).
- That a model "designs patterns" (the model picks recipe IDs and parameters).
- That all garments are supported (Level 1 woven shirt is the planned flagship, verified only after P0 passes; others are limited or inspiration only).

## needs-human

- Confirm 2027 rules, criteria, weights, time limit and deadline on the official portal (Kireeti, Delfine).
- Run the physical make, record measurements (Narthananilaa).
- Recruit a tailor and obtain consent (Delfine).
- Choose presenters; rehearse; record the fallback demo.
- Approve outline (A3).
