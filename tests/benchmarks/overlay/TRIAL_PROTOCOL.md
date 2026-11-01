# Physical overlay trial protocol (for founders to run)

Purpose: measure how far the displayed cut overlay is from independently measured marks (blueprint 6.3). No tolerance is assumed here; the team sets it (H-02) with the sewing expert.

## Setup
- Garment: your own or a consented sample, laid flat on a contrasting surface. No real people's photos or body data go in the repo.
- Ruler: straight steel ruler or printed marker on the same plane as the garment.
- Landmarks: at least 3 non-collinear points plus the ruler, spread over the garment (5 or more allows perspective).

## Conditions (vary one at a time, record each)
- Phones: at least two different models; keep the zoom setting fixed and note it.
- Camera tilt: 0, 15, 30 and 45 degrees from vertical.
- Fabric: plain woven, textured or patterned, dark, and a slippery or shiny one.
- Also: wrinkled vs flat, a partly hidden ruler (expect rejection), and marks far outside the landmark spread (tests extrapolation, which the code does not limit).

## Independent measurement
1. Before photographing, mark 6 or more test points on the fabric with chalk. Measure each from the origin landmark with a steel ruler or caliper along x and y (mm, to 0.5 mm). A second person re-measures 20% of marks.
2. Photograph with the ruler in frame. Run app calibration with corrected landmark points.
3. Mark each chalk point's centre in the photo (observed px) without looking at the overlay.
4. Record the overlay's displayed px for the same plane coordinates.

## Record
CSV with the columns listed in `overlay_qa.py`, `synthetic=false`. Include rejected trials with their reason; they are counted, not scored.

## Report
Run `python overlay_qa.py trials.csv`. Quote median and worst-case error as n/N together with the conditions. Do not claim accuracy beyond the trials run.
