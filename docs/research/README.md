# Research kit

Tools for the founders' customer and tailor conversations. Prepared by D7 Research Ops; approver: Delfine. Nothing here contacts anyone. Founders run every session.

## The loop

1. **Recruit.** Use `screener.md` (Google Form). Assign a participant code (`P01`, `T01`) at the first contact and log it in the tracker (`tracker-columns.md`). Names and contact details live only in the founders' private tracker, never in this repo.
2. **Consent.** Read `consent-form-draft.md` aloud or send it with the form. Record consent in the tracker. Sessions do not start without it. The form is a DRAFT until supervisor/ethics review (human task H-05).
3. **Run the session.** Customers: `customer-interview-guide.md` (30 min). Tailors: `tailor-interview-guide.md`. App tests: `usability-session-script.md`. One founder asks, the other (or the same founder afterwards) fills the note slots.
4. **De-identify and upload.** Within 24 hours, replace names, places, shop names, handles and any identifying detail with codes. Save as `docs/research/notes/<code>-<yyyy-mm-dd>.md` using `insight-template.md` section A. Raw audio, photos and contact details stay out of the repo and are deleted per the consent form.
5. **D7 tags insights.** D7 reads de-identified notes, fills `insight-template.md` section B (tag, quote, codes, count with denominator), and writes a summary per batch of sessions.
6. **Backlog issues.** Each actionable insight becomes a GitHub issue labelled `user-feedback`, citing the participant codes. Product issues route to the owning agent (mobile → Delfine's agents, feasibility → Narthananilaa's, API → Kireeti's).
7. **L0 validation log.** L0 receives the insight summary and updates the validation log: what was learned, how many of how many, what it changes. Negative results stay in.

```
founder session -> de-identified notes -> D7 tags -> user-feedback issues -> L0 validation log
```

## Files

| File | Use |
|---|---|
| `screener.md` | Recruiting form questions |
| `consent-form-draft.md` | DRAFT participant consent |
| `customer-interview-guide.md` | 30-minute discovery interview |
| `tailor-interview-guide.md` | Tailor/alterer interview, pilot and LOI |
| `usability-session-script.md` | Observed app tasks and metrics |
| `insight-template.md` | Note and insight format |
| `tracker-columns.md` | Google Sheet columns |

## Rules

- Participant codes only. `P` = customer/user, `T` = tailor. Numbers are never reused.
- Report counts with denominators (e.g. "6 of 9 customers", not "most"). Early sessions are a small, non-random sample: say so, do not generalise.
- The earlier team survey (n=25: 24/25 beginners or no sewing experience, 17/25 had rejected second-hand clothes over fit, 12/25 would consider finding a tailor via the app) is the starting hypothesis, not a finding to confirm. Do not mention it to participants.
- No guarantee language in any script or note ("perfect fit", "guaranteed"). Describe the product as producing redesigns that passed checks, with approximate previews.
- Do not show participants real user photos or take body measurements in sessions unless consent covers it; use synthetic or the participant's own garment with consent.
- Never contact participants from this repo or via agents.

## needs-human

- H-05: supervisor/ethics review of `consent-form-draft.md` before any session.
- Founders create the Google Form and Sheet from `screener.md` and `tracker-columns.md`.
- Founders run all sessions, collect consent, de-identify notes and delete raw recordings.
