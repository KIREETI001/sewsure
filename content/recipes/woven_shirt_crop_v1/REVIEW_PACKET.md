# Review packet: woven_shirt_crop_v1 (draft 1.0)

For the human sewist reviewer (task H-02, lead: Narthananilaa).
This recipe was drafted by an AI agent. Nothing here has been tested on a real shirt yet. Please read `recipe.yaml` and the six files in `../lessons/`, then fill in a decision for every item below.

**How to use this packet:** for each item, write one of `accept`, `change` or `reject`, and add a note if you pick `change` or `reject`. Only a named human sewist can move the recipe from `draft` to `reviewed`. Do not change `status` in the YAML until every item has a decision.

Where numbers are shown (30, 10, 20 mm) they are draft defaults from the project plan's worked example, not tested values.

## A. What the recipe does (summary)

Cut a straight line across a non-stretch woven button-up shirt, then finish the bottom edge with a double-fold hem (machine or hand). The cut line is `finished length + hem allowance` below the shoulder landmark. The app works out that number. This recipe only uses it.

## B. Assumptions to confirm

| # | Assumption in the draft | Where | Decision (accept / change / reject) | Notes |
|---|---|---|---|---|
| 1 | Hem allowance default is **30 mm** (the app lets the user change it) | `parameters.hem_allowance_mm` | | |
| 2 | Allowance splits into a **10 mm first fold** and a **20 mm second fold**, so the visible hem is 20 mm deep and the raw edge is hidden | `press_folds` | | |
| 3 | If the user picks a different allowance, folds change in proportion (not defined yet). Which rule should apply? | `parameters` | | |
| 4 | No separate seam or raw-edge finish is needed, because the double fold encloses the raw edge | whole recipe | | |
| 5 | Landmark: top of shoulder where it meets the collar, measured straight down the front. Is this the right landmark for a button-up and easy for a beginner to find? | `measure_landmark` | | |
| 6 | The back is marked separately from the same shoulder landmark. Is that reliable on a shirt with a curved or longer back hem? | `mark_back_line` | | |
| 7 | Chalk dots at five places on the front (near both side seams, near both edges of the button strip, and one more), then a ruler line. Is this the right number of points? | `mark_front_dots` | | |
| 8 | Ruler checkpoint measures at three places, front and back, before the cut. Enough? | `checkpoint_before_cut` | | |
| 9 | The shirt is cut while buttoned, front first, then back. Is this safe and tidy, or should it be cut unbuttoned? | `cut_along_line` | | |
| 10 | After the cut, no trimming step is offered. Small unevenness is handled in pressing. When should the user stop and use the tailor route instead? | `checkpoint_after_cut` | | |
| 11 | Wash and dry before measuring | `prepare_wash` | | |
| 12 | Machine hem: straight stitch about **2 mm** from the inner folded edge, with backstitches at start and end | `hem_machine` | | |
| 13 | Hand hem: slip stitch, picking up one or two threads of the shirt, stitches about **6 mm** apart (lesson text) | `hem_hand`, lesson | | |
| 14 | Both hem options are offered as equal choices. Does either one need extra warning? | `option_group: hem_method` | | |
| 15 | Eligible fabrics: non-stretch woven, for example cotton poplin or linen blend. Is the list right? Are very thin, slippery or heavy fabrics (silk, satin, denim) excluded? | `eligibility` | | |
| 16 | Not eligible: pocket, pleat, vent or seam crossing the cut line, and a cut line through a button or buttonhole | `eligibility.not_eligible` | | |
| 17 | Wording for each step suits a beginner and has no steps that need more skill than "Beginner with practice" (2 out of 5, author estimate) | `difficulty` | | |

## C. Tools and alternatives

| Tool | Alternatives listed | Decision | Notes |
|---|---|---|---|
| Ruler at least 50 cm | Long tape measure with a straight edge | | |
| Tailor's chalk or chalk pencil | Washable marker; dry soap on dark fabric | | |
| Sharp fabric scissors | Rotary cutter and mat | | |
| Pins | Sewing clips | | |
| Iron and pressing surface | None | | |
| Optional: machine, hand needle, seam gauge | Card marked with fold depths | | |

Question: is a seam gauge or card strictly needed to get the 10 mm and 20 mm folds even? Is the ruler enough?

## D. Risks for beginners (please add or remove)

| # | Risk | What the draft does about it | Decision | Notes |
|---|---|---|---|---|
| R1 | Cutting is permanent. A wrong mark makes the shirt too short. | Ruler checkpoint before the cut; user ticks it in the app | | |
| R2 | Reading the landmark differently from the app. | App asks user to enter measured length and re-check | | |
| R3 | Curved or shirt-tail hems become a straight line, which may look different from the original. | Not explained in the draft. Should the app warn about this? | | |
| R4 | Fabric shifts or stretches while marking, especially along the bias or in loose weaves. | "Lay flat and smooth" step only | | |
| R5 | Chalk or marker may not come out. | Chalk is listed first | | |
| R6 | Iron too hot burns the fabric or melts blended fibres. | Lesson tells the user to follow the care label | | |
| R7 | Needle or pin injury, sharp scissors. | Not covered beyond the tools list. Add a safety line? | | |
| R8 | Thin or slippery fabric folds badly and slips under the foot. | Not covered. Exclude or add a tip? | | |
| R9 | Hem puckers or twists. | Pressing and pinning steps | | |
| R10 | Finished length differs from the target by a few millimetres. | "Verify" step records the real number. The app does not adjust it. | | |

## E. Missing things only you may know

List anything a beginner will get wrong that this draft does not mention:

1. ____________________________________________
2. ____________________________________________
3. ____________________________________________

## F. Do the lessons match the recipe?

| Lesson | Practice task suitable? | Decision | Notes |
|---|---|---|---|
| Measure a flat shirt from a landmark | | | |
| Mark a straight cut line | | | |
| Cut woven fabric cleanly | | | |
| Press a double-fold hem | | | |
| Straight stitch practice on scrap | | | |
| Hand slip stitch for a hem | | | |

## G. Sources and rights

No third-party text, photos, video or diagrams are used (`rights.yaml`). The text was written from general sewing knowledge. Please say if any wording is too close to a published source.

## H. Physical make (P0)

The first physical make follows this recipe. Record every step where the maker had to reinterpret what was written. The recipe will be revised and a new version issued. Released versions are never edited.

## I. Sign-off

Reviewer name: ________________________________

Role or sewing experience: ________________________________

Date (YYYY-MM-DD): ________________

Overall decision (circle one): **approve as reviewed** / **approve with changes listed above** / **reject, redraft**

Signature or written confirmation: ________________________________

Changes required before status can become `reviewed`:

____________________________________________________________

____________________________________________________________

Reviewer name for the `reviewed_by` field: ____________________  Date for `reviewed_on`: ____________________

---

*Prepared by agent N5 (Recipe Author). Status of recipe: `draft`. Nothing in this packet confirms any outcome for a real garment.*
