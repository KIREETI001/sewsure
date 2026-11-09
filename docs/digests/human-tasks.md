# Human-only tasks

Tasks that agents must not do: sewing, measuring, merges, accounts, consent, contacting people, submissions. Maintained by L0; each daily digest lists the ones due in the next 72 hours.

**This file is the single list of H-task IDs.** Any other file that cites an `H-NN` ID must use the meaning here. IDs are never reused: a retired ID stays in the table with a pointer.

Last updated: 2026-11-01. Dates are proposed by L0 unless marked official. Where a due date passed with no record of completion, the task shows the original date and a re-proposed date. "Open" means nothing in the repo shows it is done; tell L0 if it was done off-repo.

**Fixed deadline:** FYP interim report and video presentation, submit to supervisor(s) and examiner, **10 Nov 2026** (official, NTU EEE FYP deadlines page, FYP 2026 S1 column).

**Merging:** `main` requires a PR but no approval, so any founder can merge any PR (root `CLAUDE.md`, #16). Agents never merge.

## Do these first

| ID | Task | Owner | Next due | Unblocks | Status |
|---|---|---|---|---|---|
| H-04 | **First shirt make.** Ruler-check the marks against the dimensioned cut plan, cut, sew the hem, measure the result, record deviation in mm with photos (§17.3 record; kit and template in #17) | Narthananilaa (lead), all | **Wed 4 Nov 2026, proposed** (was Sun 1 Nov, missed) | **P0 gate**, N6, interim report status | open, overdue |
| H-02 | **Sewist sign-off.** Name the sewist or supervisor who reviews the crop recipe and construction sequence (§8.2), get their decisions on `REVIEW_PACKET.md` and their sign-off with a date, and change the recipe status from `draft` to `reviewed`. Same meaning as `content/recipes/CLAUDE.md` and #11 | Narthananilaa | Name reviewer **Mon 2 Nov 2026** (was 29 Oct, missed); sign-off **Tue 3 Nov 2026**, before the H-04 cut | G1, H-04, D01 approval | open, overdue |
| H-07a | **Accept the GitHub repo invite** for @vanilaa23. Still pending on 1 Nov (GitHub invitations API). Created 27 Oct; GitHub's documented 7-day expiry would fall on 3 Nov, so Kireeti re-sends it if it lapses. Delfine's is accepted | Narthananilaa; Kireeti if re-send is needed | **Mon 2 Nov 2026** | Narthananilaa working in the repo | open, overdue |

## All other tasks

| ID | Task | Owner | Next due | Unblocks | Status |
|---|---|---|---|---|---|
| H-01 | Agree D01 first recipe (woven button-up crop, landmark, hem finish) at A3 and record it in `docs/decisions.md` via an L0 PR. The draft recipe and engine merged without this record | Narthananilaa (lead), Kireeti, Delfine | Mon 2 Nov 2026 (was 29 Oct, missed) | H-02, contract freeze, P0 | open, overdue |
| H-03 | Choose the real woven shirt and hand-measure it: landmarks per D01, repeat readings in mm and their variation (§17.3). L0 proposes at least 3 readings per landmark. Keep the record off-repo unless consented; give N1/K1 only synthetic or consented numbers | Narthananilaa | Mon 2 Nov 2026 (was 29 Oct, missed) | H-04, P0 E5 | open, overdue |
| H-05 | Supervisor ethics/consent review of D7's consent form (D12), then A3 agreement, before any user or tailor session or outreach interview. Same meaning as #3 | Delfine (lead), all | Wed 4 Nov 2026 | D7 sessions, D9 outreach, validation log | open |
| H-06 | Confirm the Android test device and the Expo / EAS account (D10) | Delfine | Mon 2 Nov 2026 (was 30 Oct, missed) | K5 EAS build, P0 E4 | open, overdue |
| H-07b | Create the `needs-human` label (still missing, 1 Nov). Check and merge PRs from the digest's review queue | Kireeti (label); any founder (merges) | Mon 2 Nov 2026, then daily | Agent task routing, every merge | open |
| H-08 | *Retired 2026-10-28.* Was "ethics/consent"; merged into **H-05**. #8 cites H-08 with that meaning; read it as H-05 | — | — | — | retired |
| H-09 | Check Imagine Cup 2027 rules and deadlines on the official portal; record what is official vs internal (D13, R10) | Kireeti | Wed 4 Nov 2026 | D8 pitch (#13), D13 | open |
| H-10 | FYP interim report and video: (a) approve D8's video script before filming, after X2's blocking issues are fixed (#13 films 4–7 Nov); (b) review X3's report draft (#8); (c) record the video; (d) fill the NTU GAI declaration form; (e) submit. Also agree one evidence-freeze date for the report and video, and answer audit Q1 and Q4 | Each student (Kireeti, Narthananilaa, Delfine) | (a) **Tue 3 Nov 2026**; (b) Thu 5 Nov 2026; (e) **submit Tue 10 Nov 2026** | FYP interim milestone | open |
| H-11 | Confirm Azure subscription, credits and model deployment access; set the spend cap (D08, D11). Was H-05 in the first version of this list | Kireeti | Mon 2 Nov 2026 (was 30 Oct, missed) | K3 live call, K5 deploy, K7 | open, overdue |
| H-12 | Set the calibration tolerance (mm) above which the overlay falls back to the dimensioned diagram. N4 is now running, so this is needed sooner. `packages/feasibility/CLAUDE.md:22` still calls this "H-02"; that reference should become H-12 (A3 path, founder change) | Narthananilaa | Before N4's overlay trial (date to be set by Narthananilaa) | N4, D4 | open |
| H-13 | Review and approve the ease bands, uncertainty values and sources in `fit/ease_ranges.json` (#20). They are unverified placeholders: `status: provisional`, `approved_by: null`, `source_checked: false` | Narthananilaa | Wed 4 Nov 2026 (proposed) | N3 fit results (#20), D3 fit summary | open |

## ID changes

**2026-11-01:** H-07 split into H-07a (accept invite) and H-07b (label and merges). Its old parts on approving and merging #1 are finished: #1 merged and approvals are now optional (#16).

**2026-10-28:** the first version of this list (#2, commit `008bd82`) used different numbers. X1 found they collided with `main` and other PRs.

| Task | Old ID | New ID | Why |
|---|---|---|---|
| Sewist/supervisor review | H-03 | H-02 | `main` (`content/recipes/CLAUDE.md`) and #11 already use H-02 |
| Choose and measure the shirt | H-02 | H-03 | Swap with the above |
| Ethics/consent | H-08 | H-05 | #3 already uses H-05 |
| Azure access and spend cap | H-05 | H-11 | Frees H-05 for consent |
| Calibration tolerance | (none) | H-12 | `main` (`packages/feasibility/CLAUDE.md`) uses H-02 for this too |
