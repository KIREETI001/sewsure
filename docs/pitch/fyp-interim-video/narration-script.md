# FYP interim video: narration script (draft v0)

Status: DRAFT for Delfine's approval (A3: all three founders). Not yet cleared by X2. Written 28 Oct 2026 for submission on 10 Nov 2026 with the interim report.

Format follows the NTU suggested interim report: 1 Introduction, 2 Work done so far, 3 Future work, 4 Conclusion (source: `SuggestedFormatInterimReport.pdf`). Deadline source: `fyp deadlines.pdf` (FYP 2026 S1: Interim Report and Video Presentation, 10 Nov 2026).

## How to read this file

- Target length is **9:00** (allowed range 8:00 to 10:00, an assumption, not a confirmed NTU limit; see README open question 1).
- `[C-nn]` after a line points to the claims register row that supports it (`../claims-register.md`). A line with no tag makes no factual claim.
- `[SLOT-n]` is text that depends on evidence that does not exist yet. The default wording beside each slot is the honest "not yet" version and is safe to record as is. Swap in the evidenced version only when the listed evidence exists and X2 has cleared it.
- Everything marked **planned** is not done. The speaker must say "planned" or "we have not yet" aloud, not only show it on screen.
- Word budget: about 140 spoken words per minute with pauses for b-roll. Count is recomputed at the bottom.

## Speakers (split by area, from root `CLAUDE.md` ownership table)

| Speaker | Area | Segments |
|---|---|---|
| Delfine (D) | Mobile app, UX, research | S0, S1a, S3c, S2c |
| Kireeti (K) | Platform, backend, AI, release | S1b, S1c, S2a, S3a |
| Narthananilaa (N) | Garment rules, feasibility, evidence | S2b, S2d, S3b |
| All three | Conclusion | S4 |

---

## S0 Cold open (0:00 to 0:25) | Delfine

> **[D, over the real shirt on a table, ruler and chalk beside it]**
> "This shirt is already in someone's wardrobe. It is too big, and it will probably stay there. We are three students building SewSure, an app that tries to close the gap between 'I have an idea for this garment' and 'I can actually make it'. This is our Final Year Project interim presentation."

(~55 words)

## S1 Introduction and objectives (0:25 to 2:40)

### S1a Problem and evidence (0:25 to 1:10) | Delfine

> "We ran a small exploratory survey of 25 people. It is a small, non-representative sample, so we treat it as a direction, not a result. Twenty-four of the 25 had no sewing experience or were beginners [C-01]. Seventeen had rejected second-hand clothing because of fit [C-02]. Twenty-one rated our proposed tool four or five for usefulness [C-03], and that was a description of a tool, not a working product. Twelve would consider finding a tailor through the app [C-04].
> The pattern we heard was the same: people have ideas, but an image does not tell you whether the design can be cut from the fabric you have."

(~115 words)

### S1b What SewSure is and the objectives (1:10 to 2:10) | Kireeti

> "SewSure is a mobile app we are designing. The user photographs a garment they own, says what they want, and confirms measurements. The app then aims to offer up to three redesigns that pass the feasibility checks we have implemented, and then a cut guide with DIY steps, or a brief a tailor can quote from [C-05].
> The key idea is a split of roles. A generative model may propose a design from an approved list of recipes. It never invents pattern geometry. A deterministic feasibility engine checks the numbers, in millimetres, and only that engine can set a design's status [C-07].
> Our objectives for this project are: one: prove a single measured transformation on a real woven shirt, from measurement to cut plan to a physical make. Two: connect it into a mobile prototype. Three: report what passes, what fails and what we got wrong, with denominators. [C-06]"

(~140 words)

### S1c Scope, plan and purpose of this video (2:10 to 2:40) | Kireeti

> "Scope is deliberately narrow. Level one is oversized woven button-up shirts. Jersey tees are limited and conditional. Everything else is inspiration only, with no cut plan [C-12]. There are no payments in the first version.
> Our plan runs in phases, from proving one transformation, to a connected alpha, to integration, testing, and submission preparation. The dates are internal and provisional [C-23]. This video reports honestly where we are against that plan."

(~85 words)

---

## S2 Work done so far (2:40 to 6:40)

### S2a Repository, agent workflow, contract first (2:40 to 3:50) | Kireeti

> "What exists today in our repository is a monorepo with a defined structure: mobile app, API service, a standalone feasibility package, a shared contracts package, recipes, and benchmarks [C-09].
> We also use AI coding agents, supervised by us. There are 29 agent definitions, each limited to the folders it may edit, and project hooks that block edits to secrets and production infrastructure [C-09]. Agents work in branches and open pull requests. They cannot merge. A human code owner approves every change [C-10]. We will declare this assistance on the NTU generative AI form [C-28].
> Our rules are written down: lengths in millimetres, design status set only by the feasibility engine, revisions never edited in place, and no guarantee language anywhere [C-11].
> [SLOT-1] Default: 'The shared API contract and the first service code are in progress and are not yet merged.' Replace only if the contract PR is merged by recording day, naming it."

(~150 words)

### S2b Feasibility engine and the honest rejection (3:50 to 5:20) | Narthananilaa

> "My part is the rules: what can physically be cut from a shirt, and when the answer is no.
> The design, from our blueprint, is that for a shirt crop the engine takes the original length, the finished length wanted, and a hem allowance, and works out where to mark the cut. The numbers on screen are the illustrative ones from our plan, not measurements [C-13].
> Next is the part we care about most. When a request is impossible, the engine must say so and say why. In our plan's example, a peplum needs a strip about 140 centimetres by 18, but the leftover fabric yields about 112, so it is rejected and a shorter, less full option is suggested [C-14]. That is an illustrative example. A peplum is a later transformation that still needs proof.
> [SLOT-2] Default: 'The engine and its first tests are being written now. We do not yet have a passing test suite to show.' Evidenced version, only if the N1 and N2 PRs are merged: show the real test run, name the number of cases and the number passing out of the total [C-17]."

(~165 words)

### S2c App screens and research (5:20 to 6:20) | Delfine

> "On the app side, these screens are mock-ups made from our design plan. They are labelled mock-up on screen, because they are not connected to the engine yet [C-20]. You can see capture, measurement guide, a result card with its status, and a cut guide with a ruler check.
> One rule shapes the design: an unverified design must never reach a 'safe to cut' screen. Previews are labelled approximate [C-25], and the result list never assumes there are three options.
> For research, we have the survey I described. [SLOT-3] Default: 'Interviews and usability sessions with real users and tailors are planned, with consent forms, and have not started.'"

(~110 words)

### S2d Problems encountered (6:20 to 6:40) | Narthananilaa

> "Our honest problem: our first phase, proving one measured transformation, is rated red. [SLOT-4] Default: 'We have not yet completed the physical trial of a measured shirt, so we have no predicted-versus-measured numbers to show.' We also still need to confirm which competition rules apply [C-16, C-22]."

(~60 words)

---

## S3 Future work (6:40 to 8:00)

### S3a Platform and AI | Kireeti (6:40 to 7:10)

> "Next for me: the API and the structured model pipeline, with the model constrained to approved recipe parameters. Live access to the cloud AI service is still to be verified, and so is cost per design [C-21, C-26]. All of this is planned."

(~45 words)

### S3b Feasibility and evidence | Narthananilaa (7:10 to 7:40)

> "Next for me: the constraint test suite, proposed at 24 cases, and four planned physical makes where we compare predicted and ruler-measured dimensions [C-17, C-18]. We will report false approvals and failures, not hide them."

(~40 words)

### S3c App, users and tailors | Delfine (7:40 to 8:00)

> "Next for me: connecting the screens to real results, usability sessions with eight to twelve participants as a proposed target, and a small test with two or three tailors reading a brief and quoting [C-18, C-19]. These are targets, not results."

(~45 words)

---

## S4 Honest conclusion (8:00 to 9:00) | all three, one line each, then Kireeti closes

> **[N]** "Progress so far is mostly foundations: scope, plan, rules and repository structure. [SLOT-5] Default: 'We do not yet have a measured, physically tested result.'"
> **[D]** "That means every claim about accuracy, and about whether people can follow our steps, is still untested."
> **[K]** "Our first priority is to pass the first phase gate: one real shirt, a measured cut plan, and an honest comparison with what we sewed. If it fails, we stop widening scope, and we say so in the report.
> We hope to take SewSure to the Imagine Cup 2027, if we are eligible and the rules allow it. We have not confirmed that yet [C-22]. Thank you."

(~150 words)

---

## Totals

Draft narration is about 1,100 words. At ~140 wpm that is about 7:50 of speech, leaving about 1:10 for b-roll silences and screen holds inside a 9:00 runtime. If the founders want 8:00, drop S1c's second paragraph and S3a; if 10:00, add a live walkthrough of the repo PR list (planned, only if PRs exist).

Run `wc -w` on the quoted lines before recording to recompute.

## Read-aloud rules

- Never say "guaranteed", "perfect fit", "precision", "100% accurate", "safe to cut" about an output of the app.
- Say "planned", "proposed", "mock-up", "illustrative" aloud wherever the corresponding label is on screen.
- Do not read any number that is not in the claims register with a source and denominator.
