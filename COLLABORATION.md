# Working together: Claude and ChatGPT on SewSure

This file is the shared rulebook for every AI assistant working in `KIREETI001/sewsure`. Founders set the priorities and make the merges. Assistants prepare the work.

Last updated: 9 Nov 2026. Update it through a PR when the rules change.

## Why this file exists

Claude Code is held to the project rules by hooks in `.claude/`. **Those hooks do not run for ChatGPT.** ChatGPT has to follow the same rules by choice, and GitHub only enforces one of them: `main` needs a PR. Nothing technical stops a merge, an approval or a leaked secret.

## The rules

These apply to every assistant.

1. Read the root `CLAUDE.md` and the `CLAUDE.md` nearest the files you touch. They are project rules, not Claude-only rules.
2. Work on a branch and open a PR. Never push to `main`.
3. **Never merge, approve, or close another author's PR.** Founders merge. Do not turn on auto-merge.
4. Never force-push a branch you did not create.
5. Design states are set only by `packages/feasibility`. The AI model, API and app never set or upgrade one.
6. Lengths are stored in millimetres, with origin and `confirmed_at`. Convert to cm only in the UI.
7. Revisions are immutable. An edit creates a new revision.
8. API and record shapes change only in `packages/contracts`, with a change note and an updated contract test. Tell the consuming owner.
9. No secrets, keys, real user photos or body measurements in the repo, prompts or logs. Use synthetic or consented data. Do not read `.env` files or keystores.
10. No guarantee wording, such as "guaranteed fit", "perfect fit" or "100% accurate". Every number in docs or pitch needs a source and a denominator.
11. Do not edit `infrastructure/prod/`. Do not create, change or delete real Azure resources. Write Bicep and runbooks, and a founder runs them.
12. Do not send messages, publish, submit to stores or contact people. Draft it and list it for a founder.
13. Stay in your task's paths. If it needs a change elsewhere, say so in the PR.
14. Report honestly. State what you ran, what you did not run and what failed. Never invent a result, and never describe mock data as evidence about a real garment.

## Who does what

| Who | Does |
|---|---|
| Kireeti | Platform, API, Azure, AI, cloud spend, release. `services/`, `infrastructure/`, `.github/workflows/` |
| Narthananilaa | Garment rules, engine, recipes, evidence. `packages/feasibility/`, `content/recipes/`, `tests/benchmarks/`, `docs/evaluation/` |
| Delfine | Mobile, UX, research, pitch, website. `apps/`, `docs/research/`, `docs/pitch/` |
| All three | The shared contract in `packages/contracts/` |
| ChatGPT | Default for implementation and first drafts from the task board, to save Claude credits |
| Claude | Review of risky changes, cross-area coordination, and work a founder asks for specifically |

`.claude/agents/*.md` holds a role brief for each area. Either assistant can follow one, for example "work as K2 API Builder", including its path limits.

## How to tell the assistants apart

Every PR on this repo shows `KIREETI001` as the author, so the account says nothing about who did the work.

- Branch: `chatgpt/<short-task>` or `claude/<short-task>`
- PR title starts with `[ChatGPT]` or `[Claude]`
- Commit message ends with `Agent: ChatGPT` or the assistant's own co-author line

## Starting a session

1. Fetch the latest `main`.
2. Read this file, `HANDOVER.md`, and the root `CLAUDE.md`.
3. List the open PRs and read the last comment on anything related to your task.
4. Pick the top unclaimed task your founder approves. A task is **claimed** once a draft PR for it exists.
5. Open the draft PR straight away, before doing the work, and name the files you expect to touch.

## While working

- One task, one branch, one assistant. If another open PR touches the same files, stop and tell the founder.
- Keep PRs small and easy to check.
- Base your branch on `main`. Stack on another PR only if it cannot be avoided, and say so at the top of the PR.
- Merge `main` into your branch to update it, rather than rebasing a shared branch.
- Push early and often, because a session can end at any time. The draft PR is the record of progress.

## Finishing a session

Every PR needs a user story, plus a test or evidence. At the end of each session, even an unfinished one, post this as a PR comment.

```markdown
## Handoff
**Agent:** ChatGPT or Claude
**Commit:** <short sha>
**State:** done | partly done | blocked
**What changed:**
**What I ran, with results:**
**What I did not run:**
**Next step, for whoever picks this up:**
**Needs a founder:** <decision or task, or "nothing">
```

## Review between assistants

The assistant that wrote a change does not review it.

| Change | Before a founder merges |
|---|---|
| Docs, tests, small fixes | CI passes |
| `services/`, `apps/`, `infrastructure/staging/` | The other assistant reviews, if credits allow |
| `packages/contracts/`, `packages/feasibility/`, anything affecting a design state, a cut plan, auth or personal data | The other assistant reviews, and the owning founder is told |
| Report, pitch, website or any public claim | Claims check against the repo: every number and status statement |

Reviewers comment only. A review ends with one verdict: safe to merge, or the exact blocker.

## What only founders do

Merging and approving PRs, sewing and measuring, sewist sign-off, ethics and consent, contacting people, creating accounts, Azure setup and spending, signing keys, store and competition submissions.

## Using credits well

- Give an assistant one task at a time, with the file paths and what done looks like.
- Point it at a PR or a file, rather than pasting long history.
- Use the handoff block so the next session does not have to rediscover anything.
- Save Claude for reviews of the high-risk rows above.
