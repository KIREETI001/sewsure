# Tracker columns (Google Sheet)

One sheet for outreach and sessions. **The sheet is private to the founders and lives outside the repo.** It may hold contact details; the repo never does. Share with the three team members only. Set an access list, no public link.

Tab 1: `Tracker`. Tab 2: `Lookups` (dropdown values). Tab 3: `Contacts`, holding names and contact details only, linked by participant code and never shared further.

## Tracker tab columns

| # | Column | Type / values | Notes |
|---|---|---|---|
| A | participant_code | text, unique | `P01`, `T01`; assigned at first contact; never reused |
| B | type | dropdown: customer, tailor | |
| C | segment | dropdown: non-sewer, beginner, intermediate, experienced, tailor-shop, tailor-home | from screener |
| D | founder | dropdown: Kireeti, Narthananilaa, Delfine | owner of the relationship |
| E | channel | dropdown: friend-network, social-post, community-group, walk-in, referral, screener-form, other | note if friend/family |
| F | status | dropdown: identified, invited, scheduled, consented, done, no-show, declined, withdrawn | |
| G | invited_date | date | |
| H | session_date | date | |
| I | session_type | dropdown: interview, usability, both | |
| J | consent | dropdown: none, verbal, written | |
| K | consent_audio | Y/N | |
| L | consent_photos | Y/N | |
| M | consent_recontact | Y/N | |
| N | notes_link | URL or repo path | de-identified note under `docs/research/notes/` |
| O | follow_up_date | date | |
| P | follow_up_reason | text, short | no personal detail |
| Q | pilot_interest | dropdown: yes, maybe, no, n/a | tailors and testers |
| R | loi_interest | dropdown: yes, maybe, no, n/a | tailors only; record only, never sign in session |
| S | wtp_signal | text | e.g. "free only", exact amount stated + currency |
| T | withdrawal_requested | date | triggers deletion check |
| U | deletion_done | date | audio, photos, notes, contacts removed |
| V | raw_data_delete_by | date | audio/photo deletion deadline |
| W | insights_tagged | Y/N | set by D7 after tagging |

## Contacts tab columns (not in repo)

participant_code, name, contact_method, contact_value, preferred_time.

## Conditional formatting suggestions

- Highlight `follow_up_date` in red when earlier than today and status is not done/declined/withdrawn.
- Highlight `raw_data_delete_by` when earlier than today and `deletion_done` is empty.
- Warn if `status` = done and `consent` = none.

## Weekly counts (for L0, founders fill each Friday)

| Week | Outreach sent | Replies | Sessions held | Customers | Tailors | Usability | Notes uploaded |
|---|---|---|---|---|---|---|---|

Target proposed for each founder: about 5 conversations per week (team plan, proposed, not a finding).
