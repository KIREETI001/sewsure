# apps/site

Static informational site and waitlist for SewSure. Plain HTML, CSS and one small script. No build step. Owner: Delfine. Agent: D9 Community & Waitlist.

## Pages

- `index.html`: home, with the today and planned status
- `how-it-works.html`: the planned flow, every step labelled planned
- `tailors.html`: planned tailor briefs and the tailor sign-up link
- `about.html`: the team and project status
- `privacy.html`: draft privacy notice (placeholders marked)
- `join.html`: customer waitlist and tailor sign-up forms

## Forms

The forms collect name, email, role and an optional area, plus a consent checkbox. They do **not** send or store anything yet. Submitting shows "Sign-ups open soon". `assets/join.js` is the only place that handles submission. Without JavaScript the forms are hidden and a notice is shown instead, so no personal data is ever put in a URL.

## Needs a human (`needs-human`)

- Connect the forms to a private store or the API (service side: K2 and K8, approved by Kireeti). Never a public sheet.
- Set the waitlist retention period and the deletion contact in `privacy.html` (two placeholders marked "to be set by the founders").
- Decide the Azure Static Web Apps deployment, including any `staticwebapp.config.json` (K5 Infra, approved by Kireeti).
- X2 review of all copy before this leaves the team.
- Delfine to approve the brand and copy.

## Checks

- No tracking scripts. No third-party assets, fonts or embeds.
- No guarantee wording. Checked with a text search for "guarantee", "perfect fit", "precision" and "100%".
- Planned items are labelled planned. Do not remove a label without a feature that is actually built.
- Open each page at phone width. The layout uses a 16px gutter and does not scroll sideways.
