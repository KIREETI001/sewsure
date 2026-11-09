# Physical make record

One record per physical make. It covers every field of the blueprint §17.3 "Physical validation record template". The machine-readable copy is [`physical-make-record.template.csv`](physical-make-record.template.csv): **copy it, do not edit the template**, and save the real file as `physical-make-NN.csv` once a human has filled it in. Procedure: [`p0-make-kit.md`](p0-make-kit.md).

**Status of data:** no make has been recorded yet. Nothing in this file is a result.

## Rules

- Lengths in **mm**. Convert to cm only when writing for readers.
- Copy readings as taken. Do not round, drop or tidy a bad reading. Keep failures and rework.
- `record_status` is `real` for a physical make a person measured. Anything invented for a test is `synthetic` and never goes in `docs/evaluation/` as evidence.
- No faces, body measurements, names or real user photos. Photos are listed by file name; the files stay in the team's private store.
- `abs_error_mm` = |actual − predicted|. The analysis script recomputes it and flags any mismatch.

## Fields (blueprint §17.3 to CSV)

One CSV **row per dimension compared**. Make-level fields repeat on each row of the same make.

| §17.3 field | Content | CSV columns |
|---|---|---|
| Source garment | Garment ID, composition, woven/knit, condition, front/back photos | `garment_id`, `composition`, `construction`, `condition`, `photo_files` |
| Manual measurements | Inputs, tools, repeat measurement variation | `tools_used`, `landmark`, `source_len_reading_1_mm`, `_2_mm`, `_3_mm` (original length, taken twice at least) |
| Requested transformation | Requested change, constraints, approved recipe, design revision ID | `requested_change`, `recipe_id`, `recipe_version`, `recipe_review_status` (`draft` or `reviewed`), `design_revision_id` |
| Predicted result | Cut positions, finished measurements, fit warning, materials | `dimension`, `predicted_mm`, `hem_allowance_mm`, `fit_warning` |
| Actual result | Finished dimensions, photos, alterations, time, rework | `actual_mm`, `photo_files`, `rework`, `rework_reason`, `time_minutes`, `notes` |
| Differences / failures | Absolute error (mm), cause, whether the system would have prevented it | `abs_error_mm`, `error_cause`, `system_would_have_prevented` (`yes`, `no`, `unknown`) |
| Participant feedback | Confidence, difficulty, observed help, instructions needing change | `maker_confidence_1to5`, `difficulty_1to5`, `help_observed`, `instructions_to_change` |
| Rights / consent | Which images may be used for demo/report, deletion terms | `consent_recorded` (`yes`/`no`), `images_allowed_for`, `deletion_terms` |
| (provenance) | Who and when | `make_id`, `record_status`, `measured_by`, `recorded_on` |

## Dimensions to record for the P0 shirt crop

Use these `dimension` values (all measured from the shoulder landmark, same side, same ruler):

| `dimension` | Predicted | Actual |
|---|---|---|
| `cut_mark_front` | Planned cut mark (finished length + hem allowance) | Landmark to chalk line, independent ruler (runbook step 6) |
| `cut_mark_back` | Same | Same, back |
| `cut_edge_front` | Planned cut mark | Landmark to cut edge after cutting (step 7a) |
| `finished_length_front` | Finished length F | Landmark to finished bottom edge (step 8, A1) |
| `finished_length_back` | F | A2 |
| `hem_depth` | Sum of the two folds (draft: 30 mm) | A4 |

Add other dimensions as needed; keep names lowercase with underscores. Cause categories to prefer (free text is fine too): `measurement_noise`, `landmark_misplaced`, `chalk_line_wobble`, `cutting_drift`, `fold_depth`, `fabric_shift`, `ruler_misread`, `recipe_draft_value`, `unknown`.

## Per-make summary (fill in after the session)

| Item | Value |
|---|---|
| Make ID | |
| Date, maker, recorder | |
| Recipe and its review status | `woven_shirt_crop_v1` draft 1.0, not reviewed unless a sewist has signed it |
| Total time (min) | |
| Number of re-marks before cutting | |
| Rework events | |
| Ruler check (G1) passed by | |
| Dimensions compared (n) | |
| Median / max absolute error (mm) | from `make_report.py` |
| What would we change? | |

## Reporting rule

With one make there is a handful of dimension errors from **one** shirt. Report them individually with their causes, together with the sample size ("n = 1 make, k dimensions"). A median or maximum from one make describes that make only. It is not an estimate of typical error and carries no confidence level.
