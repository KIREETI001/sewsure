# FYP interim video: narration script (draft v0)

Status: DRAFT for Delfine's approval (A3: all three founders). Not yet cleared by X2. Written 28 Oct 2026 for submission on 10 Nov 2026 with the interim report.

Format follows the NTU suggested interim report: 1 Introduction, 2 Work done so far, 3 Future work, 4 Conclusion (source: `SuggestedFormatInterimReport.pdf`). Deadline source: `fyp deadlines.pdf` (FYP 2026 S1: Interim Report and Video Presentation, 10 Nov 2026).

## How to read this file

- Target length is about **9:30** (re-timed 2 Nov) (allowed range 8:00 to 10:00, an assumption, not a confirmed NTU limit; see README open question 1).
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

(~21 s of speech; see Totals)

## S1 Introduction and objectives (0:25 to 3:15)

### S1a Problem and evidence (0:25 to 1:20) | Delfine

> "We ran a small exploratory survey of 25 people. It is a small, non-representative sample, so we treat it as a direction, not a result. Twenty-four of the 25 had no sewing experience or were beginners [C-01]. Seventeen had rejected second-hand clothing because of fit [C-02]. Twenty-one rated our proposed tool four or five for usefulness [C-03], and that was a description of a tool, not a working product. Twelve would consider finding a tailor through the app, in the scenario we described [C-04].
> The concerns people raised included sewing time, missing equipment, inaccurate AI patterns and fear of damaging a garment [C-35]. Our own reading is that an image alone does not show whether a design can be cut from the fabric you have."

(~54 s of speech; see Totals)

### S1b What SewSure is and the objectives (1:20 to 2:45) | Kireeti

> "SewSure is a mobile app we are designing. The user photographs a garment they own, says what they want, and confirms measurements. The app then aims to offer up to three redesigns that pass the feasibility checks the engine is designed to apply, and then a cut guide with DIY steps, or a brief a tailor can quote from [C-05].
> The key idea is a split of roles, and it is a design rule we are still building into the code. A generative model may propose a design from an approved list of recipes, but must not invent pattern geometry. A deterministic feasibility engine checks the numbers, in millimetres, and is meant to be the only thing that can set a design's status [C-07].
> Our four objectives match the interim report: a measured cut plan for one real shirt that we physically trial; a connected prototype; engine-set design states with immutable revisions; and evidence that keeps failures, using proposed targets for tests, makes and participants. These are targets, not yet shown to hold in the code [C-06]."

(~79 s of speech; see Totals)

### S1c Scope, plan and purpose of this video (2:45 to 3:15) | Kireeti

> "Scope is deliberately narrow. The planned flagship is oversized woven button-up shirts. Jersey tees are limited and conditional. Everything else is inspiration only, with no cut plan [C-12]. There are no payments in the first version.
> Our plan runs in phases, from proving one transformation, to a connected alpha, to integration, testing, and submission preparation. The dates are internal and provisional [C-23]."

(~27 s of speech; see Totals)

---

## S2 Work done so far (3:15 to 7:35)

### S2a Repository, agent workflow, contract first (3:15 to 4:50) | Kireeti

> "What exists today in our repository is a monorepo with a defined structure: mobile app, API service, a standalone feasibility package, a shared contracts package, recipes, and benchmarks [C-09].
> We also use AI coding agents, supervised by us. There are 29 agent definitions, each with a written list of the folders it may edit. A hook blocks agents from the merge and approve commands, and from editing secrets and production infrastructure [C-09]. Agents work in branches and open pull requests. `main` only accepts pull requests, and GitHub currently requires no approval. On 1 November, fourteen pull requests were merged in about two minutes from one founder's account with no approving review [C-39]; our claims audit ran on some of them only afterwards. [FOUNDER CONFIRM: who ran the merges, and whether that sentence is accurate.] We will declare this assistance on the NTU generative AI form [C-38].
> Our written rules include millimetres throughout and no guarantee language anywhere [C-11].
> [SLOT-1] As of [AS-OF DATE: set at recording; draft facts checked 1 and 2 Nov 2026], the merged work includes a first feasibility engine for one shirt crop recipe, a constraint test suite, a draft API contract, an API scaffold, an AI pipeline skeleton and the first intake screens [C-39]. Default for what is not merged: 'Connecting the API to the engine is in an open pull request and is not merged. The AI pipeline is not connected to the API yet, so nothing runs end to end with a model.' Re-check the merged and open lists on the day you record."

(~93 s of speech; see Totals)

### S2b Feasibility engine and the honest rejection (4:50 to 6:15) | Narthananilaa

> "My part is the rules: what can physically be cut from a shirt, and when the answer is no.
> For a shirt crop, the engine takes the original length, the finished length wanted, and a hem allowance, and works out where to mark the cut. The numbers on screen are the illustrative ones from our advisor deck, not measurements: an original length of 76 centimetres, a finished length of 52, a 2 centimetre hem, and a cut mark at 54 [C-13]. What the engine does is described from the merged code in `packages/feasibility` [C-39].
> Next is the part we care about most. When a request is impossible, the engine must say so and say why. In our plan's example, a peplum needs a strip about 140 centimetres by 18, but the leftover fabric yields about 112, so it is rejected and a shorter, less full option is suggested [C-14]. That is an illustrative example. A peplum is a later transformation that still needs proof.
> [SLOT-2] Default: 'A first engine for one shirt crop recipe and a constraint test suite are merged. The suite uses synthetic cases, not a measured shirt. Its automated check on main was failing on [AS-OF DATE], with a fix in an open pull request.' Drop the last sentence only if the fix has merged and main is green on recording day. Evidenced version: run the suite on recording day and read out the real passed and total counts [C-08, C-17]; the count was 27 cases and 29 checks in a CI run on PR #19's branch, reported in PR #26, not the 24 proposed."

(~83 s of speech; see Totals)

### S2c App screens and research (6:15 to 7:05) | Delfine

> "On the app side, four intake screens are merged: entry, garment capture, inspiration and measurements. They run only on sample data and are not connected to the engine [C-20]. The result card and the cut guide are in open pull requests and have not been merged. For now the cut guide is a dimensioned diagram; the on-garment overlay is planned and switched off. [SLOT-6] Show a screen only if its pull request is merged on recording day; otherwise show a card saying 'in an open pull request'.
> One rule shapes the design: an unverified design must never reach a 'safe to cut' screen. Previews will be labelled approximate [C-25], and the result list will not assume there are three options.
> For research, we have the survey I described. [SLOT-3] Default: 'Interviews and usability sessions with real users and tailors are planned, with consent forms, and have not started.'"

(~45 s of speech; see Totals)

### S2d Problems encountered (7:05 to 7:35) | Narthananilaa

> "Our first phase, proving one measured transformation, was rated red at our lead agent's audit of [L0 audit date]. None of its five evidence items was fully met, and no physical make was recorded in the repository. Its planned window ended on 1 November [C-16]. [SLOT-4] Founders only: if a physical make has happened off the repository, say so here with its date and what was measured, and give the record to X2 first. Default: 'No physical make is recorded in our repository.' We also still need to confirm which competition rules apply [C-22]."

(~27 s of speech; see Totals)

---

## S3 Future work (7:35 to 8:30)

### S3a Platform and AI | Kireeti (7:35 to 8:00)

> "Next for me: connecting the API and the structured model pipeline to the engine, and then to each other. The first part is in open pull requests, with review findings still being fixed; the second is not started. The model stays constrained to approved recipe parameters. Live access to the cloud AI service is still to be verified, and cost per design is still to be measured [C-21, C-37]. All of this is planned."

(~26 s of speech; see Totals)

### S3b Feasibility and evidence | Narthananilaa (8:00 to 8:15)

> "Next for me: extending the constraint test suite, then four planned physical makes where we compare predicted and ruler-measured dimensions [C-17, C-18]. We will report false approvals and failures, not hide them."

(~13 s of speech; see Totals)

### S3c App, users and tailors | Delfine (8:15 to 8:30)

> "Next for me: connecting the screens to real results, usability sessions with eight to twelve participants as a proposed target, and a small test with two or three tailors or makers reading a brief and quoting [C-18, C-36]. These are targets, not results."

(~19 s of speech; see Totals)

---

## S4 Honest conclusion (8:30 to 9:30) | all three, one line each, then Kireeti closes

> **[N]** "Progress so far is mostly foundations: scope, plan, rules, a first engine and first screens, all on sample data. [SLOT-5] Default: 'No measured, physically tested result is recorded in our repository.'"
> **[D]** "That means every claim about accuracy, and about whether people can follow our steps, is still untested."
> **[K]** "Our first phase did not pass by its planned date, so under our plan the app stays in demonstration mode, and we do not widen scope until it passes. Our first priority now is one real shirt, a measured cut plan, and an honest comparison with what we sew. We will report the re-plan and the result, whichever way it goes. [FOUNDER CONFIRM: re-plan date, if agreed; P-02 is open at the time of drafting.]
> We hope to take SewSure to the Imagine Cup 2027, if we are eligible and the rules allow it. We have not confirmed that yet [C-22]. Thank you."

(~57 s of speech; see Totals)

---

## Totals (re-timed 2 Nov 2026)

Spoken defaults (SLOT directions, claim tags and bracketed notes removed) count about 1,270 words including the cold open, which is about 9:05 at 140 words per minute. Per segment: S0 21 s, S1a 54, S1b 79, S1c 27, S2a 93, S2b 83, S2c 45, S2d 27, S3a 26, S3b 13, S3c 19, S4 57 (seconds of speech). With holds for b-roll and screen reads the running time is about **9:30**, inside the assumed 8:00 to 10:00 but with little slack. To reach 8:30: cut S3a and the second S2a paragraph. The earlier "about 1,100 words" figure was out of date; the raw `wc -w` of the quoted lines (1,412 before trimming) includes markers and slot directions and is not the running time.

The 2 Nov wording edits (S1b shortened, about 20 words added in S2a and S3a, one sentence added in S2c) change this by well under half a minute net; recount at the first read-through.

Re-time with a stopwatch at the first read-through; 140 wpm is an assumption.

## Read-aloud rules

- Never say "guaranteed", "perfect fit", "precision", "100% accurate", "safe to cut" about an output of the app.
- Say "planned", "proposed", "mock-up", "illustrative" aloud wherever the corresponding label is on screen.
- Do not read any number that is not in the claims register with a source and denominator.
