# Insight template

Two sections. Section A is filled by the founder after each session. Section B is filled by D7 when tagging a batch. De-identified only: participant codes, no names, places, shop names, handles, or photos.

---

## Section A — Session note (copy per session)

Save as `docs/research/notes/<code>-<yyyy-mm-dd>.md`.

```
Code: P__ / T__
Type: customer / tailor / usability
Date:
Founder:
Session length (min):
Consent: verbal / written; audio y/n; photos y/n   (details in tracker, not here)
Profile (de-identified): age band, sewing experience (none/beginner/intermediate/experienced), tools at home, second-hand wearer y/n, tailor used in last 12 months y/n

Notes by question:
  (copy the numbered question slots from the guide)

Top 3 observations:
1.
2.
3.

One surprise:

Quotes (verbatim, de-identified, max 3):
- "..."

Willingness to pay / pilot / LOI signals (exact figures, currency, conditions):

Usability metrics (usability sessions only): link table from the script

Open questions for next time:
```

---

## Section B — Insight (one per row, D7 fills)

| Field | Content |
|---|---|
| Insight ID | I-001 |
| Statement | One sentence, behaviour not opinion ("3 of 8 customers had kept a garment unworn for over a year because …") |
| Tag | one or more: `unworn-clothes`, `fit-problem`, `fear-of-ruining`, `skill-tools`, `trust-ai`, `tailor-use`, `willingness-to-pay`, `tailor-info-gap`, `tailor-quote`, `tailor-pilot`, `usability-blocker`, `other` |
| Evidence | Session codes: P01, P03, P07 |
| Count | x of n relevant sessions (n = sessions where the topic was asked) |
| Counter-evidence | Session codes that contradicted it |
| Confidence | low (<5 sessions) / medium / high; say why |
| Implication | What this could change (a hypothesis, not a decision) |
| Action | none / GitHub issue (`user-feedback`) # / L0 validation log |
| Owner | Product area: mobile, feasibility, API, content, pitch |

### Rules

- Every insight cites session codes.
- Counts have denominators. Early samples are small and non-random: no percentages below n=10; say "of n".
- Keep negative and contradicting evidence.
- Separate what people did from what they said they would do.
- Willingness-to-pay figures are stated intent, not demand evidence: label them so.
- Do not paraphrase into guarantee language.

### Batch summary template

```
Batch: yyyy-mm-dd to yyyy-mm-dd
Sessions: customers n=, tailors n=, usability n=
Top insights (with counts):
Contradictions / negative results:
Issues opened (#):
Entries for L0 validation log:
Questions to add to guides:
```
