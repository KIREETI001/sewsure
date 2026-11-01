# Risk register

Owner: L0 Lead Agent (maintains), Kireeti (approves). Reviewed every Friday in the weekly report.

Source: Technical Implementation Blueprint V0.1, §19 "Risk register and deliberate fallback order" (p. 19–20). Severity, early signal and mitigation are copied from the blueprint. The "Status" and "Current signal" columns are L0's, as of the date in the header of each review.

Last reviewed: 2026-10-28 (baseline, first run).

## Status key

- **Watching**: no early signal seen yet.
- **Signal seen**: the early signal has appeared; mitigation in progress. Link the evidence.
- **Fallback active**: the fallback has been triggered. Link the decision in `docs/decisions.md`.
- **Closed**: no longer applies. Link why.

## Register

| ID | Risk | Severity (§19) | Early signal (§19) | Mitigation and fallback (§19) | Status | Current signal (2026-10-28) |
|---|---|---|---|---|---|---|
| R01 | Pattern validity | CRITICAL | AI proposes shapes no recipe can construct | Whitelist transformations, geometry gate, narrow to one proven recipe | Watching | No AI pipeline or feasibility engine exists on `main` yet (scaffolding only). N1 and K3 started in wave 1. |
| R02 | Photo calibration | HIGH | Reference-line error drifts across phones | User landmark correction; conventional dimensioned guide | Watching | No calibration code yet. N4 is queued. No overlay measurements exist. |
| R03 | Jersey stretch | HIGH | Fit variability / seam finish unreliable | Only loose tee crop/cut-off; postpone fitted knit | Watching | Jersey is out of P0 scope (D03). N7 is gated on P0 green. |
| R04 | AI image mismatch | HIGH | Preview violates checked design parameters | Label illustrative; design-spec drawing and dimension summary first | Watching | No preview generation yet. |
| R05 | Three-person overload | CRITICAL | Backend, content and app timelines diverge | Stop extra services/accessories; protect P0-P1 critical path | Signal seen | P0 window closes 1 Nov 2026 (§12) and the FYP interim report and video are due 10 Nov 2026 (NTU EEE FYP deadlines page). Physical trial status is unknown to L0. 14 agents run in parallel, so founder review time is the bottleneck. Update 28 Oct: 15 PRs are open and none can be approved yet. Agent PRs come from the KIREETI001 account, so only Narthananilaa or Delfine can approve, and both repo invites are still pending (H-07). |
| R06 | Service access/cost | HIGH | Azure credits, deployment or model access blocked | Mock fixtures while access resolved; budget caps; alternative supported model | Watching | Azure access is unverified in the repo: no infrastructure, no smoke-test trace. K5 and K3 started in wave 1. Spend cap not yet recorded (D11). |
| R07 | No real makers | MEDIUM | Quotes only from team-created test accounts | State pilot limitation; preserve functional request workflow | Watching | Marketplace is not started (K8 and D5 queued). No tailor contacts are logged. |
| R08 | Instruction safety | HIGH | Users unsure where to cut or seam method wrong | Sewist review, repeated ruler prompts, hard no-go when info missing | Watching | No reviewed recipe in `content/recipes/` yet. N5 started in wave 1. A sewist or supervisor reviewer is not yet named (H-02). Draft recipe and review packet in PR #11. |
| R09 | Privacy / photos | HIGH | Public links or unwanted body measurement sharing | Scoped links and explicit brief consent; no shared raw profiles | Watching | No storage or auth yet. K6 is queued. The repo guard hooks block secrets (`.claude/hooks/`). |
| R10 | Submission schedule | HIGH | Official timeline differs from draft | Monitor published rules/account; internal milestone separate | Signal seen | The blueprint says Imagine Cup 2027 dates are tentative and must be checked on the official portal (§12, D13). Not yet checked (H-09). |

## Fallback order if a milestone slips (§19.1)

Apply in this order. Each step needs an A3 decision logged in `docs/decisions.md`.

1. Protect verified shirt crop + actual physical construction + accurate measured cut plan.
2. Protect mobile intake, measurement correction, design revision and basic DIY instructional path.
3. Preserve at least one independently useful AI task (structured intent parsing) with traced decisions.
4. Simplify avatars, candidate count and overlay sophistication as needed; label approximation.
5. Reduce marketplace to profiles and quote proof if full acceptance workflow slips.
6. Postpone tee expansion, accessory library, AI Search, Speech, AR, virtual try-on and progress-photo checking.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-28 | Created from blueprint §19. R05 and R10 marked "Signal seen". | L0 |
| 2026-10-28 | After X1 review: R05 signal adds the approval bottleneck; H-task IDs renumbered (see `docs/digests/human-tasks.md`). | L0 |
