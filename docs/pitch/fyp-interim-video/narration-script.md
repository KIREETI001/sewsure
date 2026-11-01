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
> "Imagine a shirt like this one, already in a wardrobe, too big, and unlikely to be worn again. (Framing device, not a claim about a specific garment.) We are three students building SewSure, an app that tries to close the gap between 'I have an idea for this garment' and 'I can actually make it'. This is our Final Year Project interim presentation."

(~55 words)

## S1 Introduction and objectives (0:25 to 2:40)

### S1a Problem and evidence (0:25 to 1:10) | Delfine

> "We ran a small exploratory survey of 25 people. It is a small, non-representative sample, so we treat it as a direction, not a result. Twenty-four of the 25 had no sewing experience or were beginners [C-01]. Seventeen had rejected second-hand clothing because of fit [C-02]. Twenty-one rated our proposed tool four or five for usefulness [C-03], and that was a description of a tool, not a working product. Twelve would consider finding a tailor through the app, in the scenario we described [C-04].
> The concerns people raised included sewing time, missing equipment, inaccurate AI patterns and fear of damaging a garment [C-35]. Our own reading is that an image alone does not show whether a design can be cut from the fabric you have."

(~115 words)

### S1b What SewSure is and the objectives (1:10 to 2:10) | Kireeti

> "SewSure is a mobile app we are designing. The user photographs a garment they own, says what they want, and confirms measurements. The app then aims to offer up to three redesigns that pass the feasibility checks the engine is designed to apply, and then a cut guide with DIY steps, or a brief a tailor can quote from [C-05].
> The key idea is a split of roles, and it is a design rule we are still building into the code. A generative model may propose a design from an approved list of recipes, but must not invent pattern geometry. A deterministic feasibility engine checks the numbers, in millimetres, and is meant to be the only thing that can set a design's status [C-07].
> Our four objectives match the interim report. One: one real, user-measured woven shirt yields a reviewed, dimensioned cut plan that we physically trial. Two: a connected mobile prototype carries a photo through to checked options and a DIY sequence. Three: design states are set only by the engine, revisions are immutable, and an unverified image never reaches a safe-to-cut screen. These are targets, not yet shown to hold in the code. Four: we evaluate with evidence that keeps failures, using proposed targets for tests, makes and participants [C-06]."

(~140 words)

### S1c Scope, plan and purpose of this video (2:10 to 2:40) | Kireeti

> "Scope is deliberately narrow. The planned flagship is oversized woven button-up shirts. Jersey tees are limited and conditional. Everything else is inspiration only, with no cut plan [C-12]. There are no payments in the first version.
> Our plan runs in phases, from proving one transformation, to a connected alpha, to integration, testing, and submission preparation. The dates are internal and provisional [C-23]. This video reports honestly where we are against that plan."

(~85 words)

---

## S2 Work done so far (2:40 to 6:40)

### S2a Repository, agent workflow, contract first (2:40 to 3:50) | Kireeti

> "What exists today in our repository is a monorepo with a defined structure: mobile app, API service, a standalone feasibility package, a shared contracts package, recipes, and benchmarks [C-09].
> We also use AI coding agents, supervised by us. There are 29 agent definitions, each with a written list of the folders it may edit. A hook blocks agents from the merge and approve commands, and from editing secrets and production infrastructure [C-09]. Agents work in branches and open pull requests. `main` only accepts pull requests; GitHub currently requires no approval, and a founder merges them [C-10]. We will declare this assistance on the NTU generative AI form [C-38].
> Our rules are written down: lengths in millimetres, design status set by the feasibility engine, revisions never edited in place, and no guarantee language anywhere [C-11].
> [SLOT-1] As of [AS-OF DATE: set at recording; draft facts checked 1 Nov 2026], fourteen pull requests were merged on 1 November, including a first feasibility engine for one shirt crop recipe, a constraint test suite, a draft API contract, an API scaffold, an AI pipeline skeleton and the first intake screens [C-39]. Default for what is not merged: 'Connecting the API and the AI pipeline to the engine is in open pull requests and is not merged.' Re-check the merged and open lists on the day you record."

(~165 words)

### S2b Feasibility engine and the honest rejection (3:50 to 5:20) | Narthananilaa

> "My part is the rules: what can physically be cut from a shirt, and when the answer is no.
> The design, from our blueprint, is that for a shirt crop the engine takes the original length, the finished length wanted, and a hem allowance, and works out where to mark the cut. The numbers on screen are the illustrative ones from our advisor deck, not measurements: an original length of 76 centimetres, a finished length of 52, a 2 centimetre hem, and a cut mark at 54 [C-13].
> Next is the part we care about most. When a request is impossible, the engine must say so and say why. In our plan's example, a peplum needs a strip about 140 centimetres by 18, but the leftover fabric yields about 112, so it is rejected and a shorter, less full option is suggested [C-14]. That is an illustrative example. A peplum is a later transformation that still needs proof.
> [SLOT-2] Default: 'A first engine for one shirt crop recipe and a constraint test suite are merged. They run on synthetic cases, not on a measured shirt.' Evidenced version: run the suite on recording day and read out the real passed and total counts [C-08, C-17]."

(~170 words)

### S2c App screens and research (5:20 to 6:20) | Delfine

> "On the app side, four intake screens are merged: entry, garment capture, inspiration and measurements. They run only on sample data and are not connected to the engine [C-20]. The result card and the cut guide are in open pull requests and have not been merged. [SLOT-6] Show a screen only if its pull request is merged on recording day; otherwise show a card saying 'in an open pull request'.
> One rule shapes the design: an unverified design must never reach a 'safe to cut' screen. Previews will be labelled approximate [C-25], and the result list will not assume there are three options.
> For research, we have the survey I described. [SLOT-3] Default: 'Interviews and usability sessions with real users and tailors are planned, with consent forms, and have not started.'"

(~125 words)

### S2d Problems encountered (6:20 to 6:40) | Narthananilaa

> "Our first phase, proving one measured transformation, was rated red at our last audit on [AS-OF DATE]. None of its five evidence items was fully met, and no physical make was recorded in the repository. Its planned window ended on 1 November [C-16]. [SLOT-4] Founders only: if a physical make has happened off the repository, say so here with its date and what was measured, and give the record to X2 first. Default: 'No physical make is recorded in our repository.' We also still need to confirm which competition rules apply [C-22]."

(~85 words)

---

## S3 Future work (6:40 to 8:00)

### S3a Platform and AI | Kireeti (6:40 to 7:10)

> "Next for me: connecting the API and the structured model pipeline to the engine, which is in open pull requests, with the model constrained to approved recipe parameters. Live access to the cloud AI service is still to be verified, and cost per design is still to be measured [C-21, C-37]. All of this is planned."

(~45 words)

### S3b Feasibility and evidence | Narthananilaa (7:10 to 7:40)

> "Next for me: extending the constraint test suite, then four planned physical makes where we compare predicted and ruler-measured dimensions [C-17, C-18]. We will report false approvals and failures, not hide them."

(~40 words)

### S3c App, users and tailors | Delfine (7:40 to 8:00)

> "Next for me: connecting the screens to real results, usability sessions with eight to twelve participants as a proposed target, and a small test with two or three tailors or makers reading a brief and quoting [C-18, C-36]. These are targets, not results."

(~45 words)

---

## S4 Honest conclusion (8:00 to 9:00) | all three, one line each, then Kireeti closes

> **[N]** "Progress so far is mostly foundations: scope, plan, rules, a first engine and first screens, all on sample data. [SLOT-5] Default: 'No measured, physically tested result is recorded in our repository.'"
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
