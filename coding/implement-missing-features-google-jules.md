---
title: "Implement Missing Features — Google Jules Edition"
description: "A senior developer prompt for implementing gaps found in a feature audit, adapted for Google Jules' async, session-and-PR workflow."
category: "coding"
tags: [implementation, feature-parity, senior-dev, google-jules, async-agent, github-pr]
compatible_models: [Google Jules]
author: "Oghenekaro Edaware"
added: "2026-07-05"
---

# Implement Missing Features — Google Jules Edition

This prompt is designed for **Google Jules**: an asynchronous agent that clones your repo into an isolated Cloud VM per session, produces a plan you approve *before* it touches any files, executes unattended, and hands the result back as a pull request rather than a chat transcript. The prompt below is written around those mechanics — one explicit approval gate, session boundaries instead of a live back-and-forth, and a PR as the actual deliverable.

Run the **Missing & Incomplete Features Audit** prompt first — this prompt consumes its output — and make sure the resulting report file is committed and pushed to the branch Jules will read from. Jules works from a cloned snapshot of your repo at session start; it can't see files you haven't pushed, and it can't be handed a file mid-session the way a chat tool can.

## Prompt

```markdown
# Implement Missing Features (Jules) — Prompt

Assign this to Jules as a session against the target repo. Paste everything below as the task description.

---

You are acting as a senior developer picking up a gap-analysis report and implementing the missing pieces properly — the way you'd want a trusted senior to do it on your own codebase: no shortcuts, no scope creep, matching the existing style so it doesn't look bolted on.

## Step 0 — Load the report

Read the most recent `/doc/missing-features-*.md` file in this repo. If it doesn't exist in your cloned snapshot, stop immediately, do not generate a plan, and report back that the Missing & Incomplete Features Audit needs to be run and its output pushed to this branch first. Do not guess at gaps yourself in this pass.

## Step 1 — Triage becomes your plan, not a side conversation

Jules only exposes one approval checkpoint before execution: the plan. Treat plan generation as the triage step, not a formality to click past.

1. In the plan, list every item from the report's **Explicit Gaps** and **Inferred Gaps** tables.
2. For each **inferred** item, re-verify it against the actual cloned code before trusting the report — reports can be stale or wrong. If you disagree with an inferred gap, state why in the plan and exclude it rather than implementing a guess nobody confirmed was wanted.
3. Group related items that should land together (e.g. "password reset" touches both the auth screen and the auth service — one unit, not two disconnected edits).
4. Order the work using the report's **Recommended Priority Order**, adjusted for technical dependency — if B requires A to exist first, A goes first regardless of stated priority.
5. **Decide session boundaries as part of the plan.** Everything in this session lands on one branch as one PR, so:
   - Keep items that touch the same files or modules in this one session — splitting them risks two parallel Jules sessions producing conflicting edits to the same file.
   - If the triaged list contains genuinely unrelated items (different modules, no shared files), say so explicitly in the plan and recommend they be run as separate Jules sessions instead, so they can execute in parallel rather than being serialized into one oversized PR.
6. If the true scope of an item is ambiguous — you can't tell what "done" looks like from the report alone — flag that in the plan and ask a clarifying question rather than narrowing the scope yourself. Ambiguous, under-specified scope is the most common way async sessions like this go wrong.
7. Present this triaged plan as your generated plan and **stop there**. Do not begin execution until you receive explicit approval in the session. Do not treat silence or a generic "continue" as approval to also expand scope beyond what was in the approved plan.

## Step 2 — Match the existing codebase, don't impose your own style

Before implementing each item:
- Search the cloned repo for the nearest existing analog (a similar CRUD flow, a similar screen, a similar service call) and follow its conventions: naming, file structure, state management pattern, error handling style, how it talks to the same backend/service layer.
- Reuse existing shared components, services, and utilities rather than writing new ones that duplicate them. If the report itself flagged duplicate/parallel implementations (e.g. two versions of a service), resolve that duplication as part of the fix rather than adding a third version.
- Match existing naming precisely. If the rest of the app calls a save action `_saveForm()`, don't introduce `_handleSubmit()` for the new one.

## Step 3 — Implement each item like a senior developer would

For every item in the approved plan:
- **Write the minimal correct implementation** for what the report described — don't expand scope, don't add speculative configurability or extra features nobody asked for.
- **Handle the failure paths, not just the happy path**: network errors, empty/invalid input, permission denials, slow responses. If the rest of the app has a pattern for this (loading states, error banners, toasts), reuse it.
- **Respect security and data-handling norms already implied by the codebase.** If the audit or documentation flagged something like a hardcoded secret, do not introduce another one in your new code, and flag existing ones you encounter rather than propagating the pattern.
- **Keep functions and files at a similar size/shape to their neighbors** — if everything else in the module is broken into small single-purpose functions, don't write one large function for the new feature.
- **Add tests if the project has a test suite.** Match the existing test style and coverage expectations; if there's no test suite at all, note that rather than inventing a new testing setup unprompted.
- **Update any type/schema definitions** the feature depends on, and check for other places that same model is used to make sure you haven't broken them.
- If a needed dependency or tool isn't in your VM and there's no reusable Environment Snapshot configured for this repo, install what you need to proceed, but note in your final report that a snapshot should be configured so future sessions start faster.

## Step 4 — Verify before moving to the next item, and before opening the PR

- Run the project's existing lint/typecheck/test commands inside your VM, and fix any failures your change introduced before continuing to the next item.
- Manually trace the user-facing flow end to end (trigger → logic → data → UI update) to confirm it actually works, not just compiles.
- Do not mark an item done, and do not include it in the PR as finished, if you had to leave a new `TODO` behind to make it "pass" — that's not implementing it, that's moving the gap.
- Only open the pull request once every item in the approved plan has been verified this way. If CI fails after the PR is opened, diagnose and fix genuine issues — don't use that loop to quietly weaken a test or skip a check just to turn CI green.

## Step 5 — Report back through the PR, not just chat

Since this session's output is a pull request, the report must live where it will actually be reviewed:

1. Write the PR description itself using the structure below, so a reviewer never has to open a separate file to know what happened.
2. Also commit a companion file to the branch at `/doc/implemented-features-<YYYY-MM-DD>.md` with the same content, so it's preserved in the repo history alongside the audit report it responds to:

```markdown
# Implemented Features — [Project Name]
Generated: [date]
Source report: [path to the missing-features report used]
Session scope: [what was included in this session vs. deferred to separate sessions]

## Implemented
| Feature | Files changed | Approach taken | Tests added/updated |
|---|---|---|---|

## Skipped or Deferred
| Feature | Reason skipped (disagreed with inference / needs product decision / blocked by dependency / recommended as a separate parallel session) |
|---|---|

## Follow-up Recommendations
[Anything uncovered while implementing that deserves its own future pass — new gaps found, tech debt touched, security items noticed but out of scope for this session, missing Environment Snapshot, etc.]
```

## Rules
- Never implement an inferred gap you couldn't actually confirm in the code — exclude it from the plan and log why instead of guessing at intent.
- Never fix more than what was approved in the plan — if you notice an unrelated bug while implementing, note it in Follow-up Recommendations rather than fixing it inline, unless the user explicitly asked you to also clean up as you go.
- Never leave the codebase in a worse or half-changed state, and never open the PR in that state — if an item turns out to be larger than expected mid-session, finish it properly or revert it before including it in the PR.
- Any change that alters an existing working feature's behavior, not just adds a new one, must be called out explicitly in the plan before execution — this is your only chance to get that confirmed before the change ships in the PR.
- If mid-session you discover the real scope no longer matches the approved plan, stop, do not silently improvise a new scope, and surface this clearly in your final report for the user to decide on a follow-up session.
```
