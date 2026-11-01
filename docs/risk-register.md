# Risk register

Owner: L0 Lead Agent (maintains), Kireeti (approves). Reviewed every Friday in the weekly report.

Source: Technical Implementation Blueprint V0.1, §19 "Risk register and deliberate fallback order" (p. 19–20). Severity, early signal and mitigation are copied from the blueprint. The "Status" and "Current signal" columns are L0's, as of the date in the header of each review.

Last reviewed: 2026-11-01.

## Status key

- **Watching**: no early signal seen yet.
- **Signal seen**: the early signal has appeared; mitigation in progress. Link the evidence.
- **Fallback active**: the fallback has been triggered. Link the decision in `docs/decisions.md`.
- **Closed**: no longer applies. Link why.

## Register

| ID | Risk | Severity (§19) | Early signal (§19) | Mitigation and fallback (§19) | Status | Current signal (2026-11-01) |
|---|---|---|---|---|---|---|
| R01 | Pattern validity | CRITICAL | AI proposes shapes no recipe can construct | Whitelist transformations, geometry gate, narrow to one proven recipe | Watching | Engine (#12) and AI pipeline skeleton (#10) are on `main`. On the #19 branch the constraint suite shows false acceptance 0/21 with synthetic inputs, but `CI Benchmarks` still fails on `main` until #19 merges. No real garment or live model output has been tested. |
| R02 | Photo calibration | HIGH | Reference-line error drifts across phones | User landmark correction; conventional dimensioned guide | Watching | N4 is running; no calibration code on `main` yet. No overlay measurements exist. Tolerance not set (H-12). |
| R03 | Jersey stretch | HIGH | Fit variability / seam finish unreliable | Only loose tee crop/cut-off; postpone fitted knit | Watching | Jersey is out of P0 scope (D03). N7 is gated on P0 green. |
| R04 | AI image mismatch | HIGH | Preview violates checked design parameters | Label illustrative; design-spec drawing and dimension summary first | Watching | No preview generation yet. |
| R05 | Three-person overload | CRITICAL | Backend, content and app timelines diverge | Stop extra services/accessories; protect P0-P1 critical path | Signal seen | Code merged (14 PRs on 1 Nov) while the physical path has no record: the P0 exit date passed with no make, no sign-off and D01 unrecorded. The FYP interim report and video are due 10 Nov 2026, 9 days away (NTU EEE FYP deadlines page), and X2 has blocked #8 and #13. Wave-2 agents are active, and six were stopped by a usage limit (R12). The approval deadlock from 28 Oct is gone (#16), but Narthananilaa's invite is still pending (H-07a). The §19 fallback is not triggered: that needs an A3 decision (P-02 in `docs/decisions.md`). |
| R06 | Service access/cost | HIGH | Azure credits, deployment or model access blocked | Mock fixtures while access resolved; budget caps; alternative supported model | Watching | Bicep and CI are on `main` (#6), but `deploy-staging` has 0 runs and no live model trace exists. Azure access unconfirmed (H-11). Spend cap not agreed (D11); `main.bicep` has a default `budgetAmount` of 50, a parameter only. |
| R07 | No real makers | MEDIUM | Quotes only from team-created test accounts | State pilot limitation; preserve functional request workflow | Watching | Marketplace is not started (K8 and D5 held until P2, 16 Nov). No tailor contacts are logged. |
| R08 | Instruction safety | HIGH | Users unsure where to cut or seam method wrong | Sewist review, repeated ruler prompts, hard no-go when info missing | Watching | Recipe `woven_shirt_crop_v1` is on `main` with `status: draft` (#11). Reviewer not named and packet not filled in (H-02). Its numbers are untested draft values (`REVIEW_PACKET.md`). |
| R09 | Privacy / photos | HIGH | Public links or unwanted body measurement sharing | Scoped links and explicit brief consent; no shared raw profiles | Watching | API scaffold is on `main` (#5). K6 threat model is in open #18; K6 tests are waiting on K2/K3 integration. Site forms and outreach are on `main` with X2 blocking issues (#7): do not publish. The repo guard hooks block secrets (`.claude/hooks/`). |
| R10 | Submission schedule | HIGH | Official timeline differs from draft | Monitor published rules/account; internal milestone separate | Signal seen | The blueprint says Imagine Cup 2027 dates are tentative and must be checked on the official portal (§12, D13). Not yet checked (H-09). |
| R11 | Merges with no required review (added by L0, not in §19) | HIGH (proposed) | PRs merge with open review findings or without a re-review | Check the review queue before merging; founders decide whether to close the shared-account route (P-03) | Signal seen | All 14 merges on 1 Nov had no approving review, as #16 allows. X2 reports 7 blocking issues on #7, and no open PR fixes them. X2 asked on #13 whether the shared-account merge route needs closing. |
| R12 | Agent usage limits (added by L0, not in §19) | MEDIUM (proposed) | Agents stop mid-task; fewer can run at once | Run critical-path agents first (K2/K3 integration); keep work committed to branches; protect P0-P1 (§19) | Signal seen | A usage limit stopped K2, K3, N4, D3, D4 and D6 on 1 Nov; they have been resumed, with no PR yet. L0 itself was also interrupted. Usage is not measured. |

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
| 2026-11-01 | After 14 merges and the missed P0 date: R01, R02, R05, R06, R07, R08, R09 signals updated. R11 and R12 added, severities proposed. | L0 |
