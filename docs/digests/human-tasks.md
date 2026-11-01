# Human-only tasks

Tasks that agents must not do: sewing, measuring, approvals, accounts, consent, contacting people, submissions. Maintained by L0; each daily digest lists the ones due in the next 72 hours.

**This file is the single list of H-task IDs.** Any other file that cites an `H-NN` ID must use the meaning here. IDs are never reused: a retired ID stays in the table with a pointer.

Last updated: 2026-10-28 (after the X1 review of PR #2). Dates are proposed by L0 from the blueprint P0 window (22 Oct – 1 Nov 2026, §12) and the NTU EEE FYP deadlines page, unless marked official.

**Fixed deadline:** FYP interim report and video presentation, submit to supervisor(s) and examiner, **10 Nov 2026** (official, NTU EEE FYP deadlines page, FYP 2026 S1 column).

**Who can approve agent PRs:** every agent PR is opened from the KIREETI001 account, and GitHub never counts an author's approval. So Kireeti cannot approve any agent PR. Approvals come from Narthananilaa (@vanilaa23) or Delfine (@delfinee), per `.github/CODEOWNERS`. Both repo invites are still pending (GitHub invitations API, 2026-10-28), so **nobody can approve anything until H-07 is done**.

| ID | Task | Owner | Next due | Unblocks | Status |
|---|---|---|---|---|---|
| H-01 | Agree D01 first recipe (woven button-up crop, landmark, hem finish) at A3 and record it in `docs/decisions.md` via an L0 PR | Narthananilaa (lead), Kireeti, Delfine | Thu 29 Oct 2026 | K1 fixture, N1 cut math, N5 recipe, P0 | open |
| H-02 | Name the sewist or supervisor who reviews the crop recipe and construction sequence (§8.2), get their sign-off with a date, and change the recipe status from `draft` to `reviewed`. Same meaning as `content/recipes/CLAUDE.md` and PR #11 | Narthananilaa | Name reviewer Thu 29 Oct 2026; sign-off before H-04 cut | G1, D01 approval, N5 recipe (#11) | open |
| H-03 | Choose the real woven shirt and hand-measure it: landmarks per D01, repeat readings in mm and their variation (§17.3). L0 proposes at least 3 readings per landmark. Keep the record off-repo unless consented; give N1/K1 only synthetic or consented numbers | Narthananilaa | Thu 29 Oct 2026 | P0 E5, N1 test fixture | open |
| H-04 | Physical trial: ruler-check the marks against the dimensioned cut plan, cut, sew the hem, measure the result, record deviation in mm with photos (§17.3 record) | Narthananilaa (lead), all | Sun 1 Nov 2026 (P0 end) | **P0 gate**, N6 | open |
| H-05 | Supervisor ethics/consent review of D7's consent form (D12), then A3 approval, before any user or tailor session or outreach interview. Same meaning as PR #3 | Delfine (lead), all | Wed 4 Nov 2026 | D7 sessions (#3), D9 outreach (#7), validation log | open |
| H-06 | Confirm the Android test device and the Expo / EAS account (D10) | Delfine | Fri 30 Oct 2026 | D2 (#14), K5 EAS build, P0 E4 | open |
| H-07 | **Approval path.** (a) Narthananilaa and Delfine accept their GitHub repo invites. (b) One of them approves PR #1 (backup code owners); Kireeti merges it. (c) Then they review agent PRs per `.github/CODEOWNERS`: Narthananilaa or Delfine for `services/`, `infrastructure/`, `.github/`, shared contract and docs; Narthananilaa for feasibility, recipes, benchmarks; Delfine for apps, research, pitch, outreach. (d) Kireeti creates the `needs-human` label | (a)(c) Narthananilaa, Delfine; (b) Narthananilaa or Delfine approve, Kireeti merges; (d) Kireeti | (a)(b) **Thu 29 Oct 2026**; (c) daily after X1 says "ready" | Every merge to `main` | open |
| H-08 | *Retired 2026-10-28.* Was "ethics/consent"; merged into **H-05**. PR #8 cites H-08 with that meaning; read it as H-05 | — | — | — | retired |
| H-09 | Check Imagine Cup 2027 rules and deadlines on the official portal; record what is official vs internal (D13, R10) | Kireeti | Wed 4 Nov 2026 | D8 pitch (#13), D13 | open |
| H-10 | FYP interim report and video: (a) approve D8's video script before filming (PR #13 films 4–7 Nov); (b) review X3's report draft (PR #8); (c) record the video; (d) fill the NTU GAI declaration form; (e) submit | Each student (Kireeti, Narthananilaa, Delfine) | (a) **Tue 3 Nov 2026**; (b) Thu 5 Nov 2026; (e) **submit Tue 10 Nov 2026** | FYP interim milestone | open |
| H-11 | Confirm Azure subscription, credits and model deployment access; set the spend cap (D08, D11). Was H-05 in the first version of this list | Kireeti | Fri 30 Oct 2026 | K3 live call (#10), K5 deploy (#6), K7 | open |
| H-12 | Set the calibration tolerance (mm) above which the overlay falls back to the dimensioned diagram. `packages/feasibility/CLAUDE.md` currently calls this "H-02"; that reference should become H-12 (A3 path, issue for the founders) | Narthananilaa | Before N4 starts (after P0 green) | N4, D4 | open |

## ID changes on 2026-10-28

The first version of this list (PR #2, commit `008bd82`) used different numbers. X1 found they collided with `main` and other PRs.

| Task | Old ID | New ID | Why |
|---|---|---|---|
| Sewist/supervisor review | H-03 | H-02 | `main` (`content/recipes/CLAUDE.md`) and PR #11 already use H-02 |
| Choose and measure the shirt | H-02 | H-03 | Swap with the above |
| Ethics/consent | H-08 | H-05 | PR #3 already uses H-05 |
| Azure access and spend cap | H-05 | H-11 | Frees H-05 for consent |
| Calibration tolerance | (none) | H-12 | `main` (`packages/feasibility/CLAUDE.md`) uses H-02 for this too |
