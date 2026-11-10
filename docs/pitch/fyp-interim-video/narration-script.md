# FYP interim video: narration script (3:00 summary, draft v1)

Status: DRAFT for the founders' approval (A3). Not yet cleared by X2. Replaces the 10-minute script of commit `331ffe5` (kept in git history). Status date: **9 Nov 2026** (Kireeti can change it). Submission with the interim report: 10 Nov 2026 (source: `fyp deadlines.pdf`).

Limit: **3:00 maximum**, confirmed by Kireeti via the lead session. The NTU documents D8 read state no video length.

## How to read this file

- `[C-nn]` after a line points to the claims register row (`../claims-register.md`). Tags, `[FOUNDER CONFIRM]` notes and headings are never read aloud.
- Every quoted line is the default wording and states only what exists on 9 Nov 2026 or is labelled not done / planned. There are no slot variants that assume a physical make: none has happened.
- Say "planned", "not done", "mock data", "sample text" aloud wherever the matching label is on screen.
- Order follows the NTU interim format: introduction, work done so far, what is not done and future work, conclusion.

## Speakers

| Speaker | Segments | Spoken words | At 140 wpm |
|---|---|---|---|
| Delfine (D) | S0, S1, S3c, S4b | 117 | 50 s |
| Kireeti (K) | S2, S3b, S4c, S5, S6b | 174 | 75 s |
| Narthananilaa (N) | S3a, S4a, S6a | 80 | 34 s |
| All three | S6c | 6 | 3 s |
| **Total** | | **377** | **162 s (2:42)** |

---

## 1 Introduction

### S0 Open (0:00 to 0:11) | Delfine, over a stand-in shirt on a table

> "We are three students building SewSure, an app meant to help turn a garment you own into a redesign you can make. This is our interim summary."

(27 words.) No claim about a specific garment.

### S1 Problem and survey (0:11 to 0:27) | Delfine

> "In October 2026 we surveyed 25 university students and friends [C-40]. It is small and not representative: a direction, not a result. Twenty-four had no sewing experience or were beginners [C-01]; seventeen had rejected second-hand clothes because of fit [C-02]."

(37 words.)

### S2 What SewSure is, and the rule (0:28 to 0:59) | Kireeti

> "SewSure is a mobile app we are designing. You photograph a garment, say what you want, and confirm measurements. It aims to offer redesigns that pass feasibility checks, then a cut guide or a tailor brief [C-05]. One rule: an AI model may only pick approved recipes, and a feasibility engine, in millimetres, is meant to be the only thing that sets a design's status. We are still building that into the code [C-07]."

(72 words.)

## 2 Work done so far (as of 9 Nov 2026)

### S3a Engine (0:59 to 1:14) | Narthananilaa

> "As of 9 November: a first feasibility engine for one shirt-crop recipe, and a suite of 27 synthetic cases [C-08]. On main, all 29 checks matched [C-08]. Synthetic means invented inputs, not a measured shirt."

(33 words.) Re-check on recording day that CI is still green on `main`; if it is not, say so instead.

### S3b API (1:14 to 1:17) | Kireeti

> "An API now calls the engine [C-39]."

(6 words.)

### S3c Demo screens (1:18 to 1:26) | Delfine

> "Demo screens run on mock data [C-20]. The word Verified on the result cards is sample text; nothing has been verified [C-20]."

(20 words.) Say the second sentence whenever the result card (M3) is on screen, with the MOCK DATA badge in frame. Do not film the edit-then-cut path.

## 3 What is not done, and agents

### S4a Not done: make, shirt, reviewer, phase 0 (1:27 to 1:40) | Narthananilaa

> "Not done: no physical make, the shirt is not chosen, and no sewist has reviewed the recipe, which is still a draft [C-41]. Our first phase, due 1 November, did not pass [C-16]."

(31 words.)

### S4b Not done: overlay, phone, interviews (1:41 to 1:55) | Delfine

> "The cut guide is a diagram only; there is no overlay [C-20]. Our phone is a Samsung S24 Ultra with the Expo build service active, but no phone run is recorded [C-42]. No interviews yet [C-41]."

(33 words.) `[FOUNDER CONFIRM: device and build service; no eas.json is on main. Cut "with the Expo build service active" if unsure.]`

### S4c Not done: pipeline, Azure (1:56 to 2:02) | Kireeti

> "The AI pipeline is not connected to the API, and Azure is not set up [C-41, C-21]."

(15 words.)

### S5 How we use agents (2:03 to 2:26) | Kireeti

> "We build with AI coding agents: 29 agent definitions, and hooks that block merge commands [C-09]. I ran all 25 merges, 14 on 1 November and 11 on 9 November, using commands an agent prepared, after approving each batch [C-44]. GitHub requires no approval, so that is process, not a technical control [C-10]. We will declare this on the NTU form [C-38]."

(58 words.) `[FOUNDER CONFIRM: "I ran all 25 merges after approving each batch" was supplied through the lead session; GitHub records only the shared account.]`

## 4 Future work and conclusion

### S6a Next (2:26 to 2:33) | Narthananilaa

> "Next: one real shirt, a measured cut plan, and an honest comparison with what we sew [C-16]."

(16 words.) Planned, not a result.

### S6b Imagine Cup (2:34 to 2:44) | Kireeti

> "Then the Imagine Cup deadline, 28 February 2027, under its official Rules. They require a legal entity, so we are not claiming eligibility [C-43]."

(23 words.)

### S6c Close (2:44 to 2:47) | all three

> "Targets are not results. Thank you."

(6 words.)

---

## Totals

- **Spoken words: 377**, counted by script on the quoted default lines (claim tags, bracketed notes and headings excluded). By speaker: D 117, K 174, N 80, all 6. This is 371 before the 2 Nov X2 edits plus 6.
- **Estimated time: about 2:51** = 162 s of speech at 140 words per minute plus about 9 s of gaps. Saying the numbers in full ("twenty twenty-six", "twenty-eight February") adds about 9 words, so **about 386 words and about 2:54** if read exactly as spoken. That is under 3:00 with about 6 s to spare.
- **140 wpm is an assumption**, not a measurement. Time a read-through with a stopwatch before filming; if it runs over, cut "This is our interim summary." and the seventeen clause in S1, with its 17/25 card.
- The segment windows above were computed before these edits and run a few seconds early; re-cut them after the stopwatch read-through.

## Read-aloud rules

- Never say "guaranteed", "perfect fit", "precision", "100% accurate", or "safe to cut" about an output of the app.
- Do not claim eligibility for the Imagine Cup.
- Do not read any number that is not in the claims register with a source and denominator.
