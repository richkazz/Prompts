---
title: "Missing Features Verification Audit — Google Jules Edition"
description: "A senior engineer prompt that cross-checks an implementation report against the original gap-analysis report to confirm what's actually complete, versus incomplete, misreported, or regressed."
category: "review"
tags: [audit, gap-analysis, verification, technical-debt, google-jules, async-agent, github-pr]
compatible_models: [Google Jules]
author: "Oghenekaro Edaware"
added: "2026-07-05"
---

# Missing Features Verification Audit — Google Jules Edition

This is the third stage of the pipeline: **Missing & Incomplete Features Audit → Implement Missing Features → this verification pass.** It takes two inputs — the original gap report and the implementation report Jules wrote when it (claimed to) close those gaps — and independently checks whether the work actually holds up. It does not trust the implementation report's own account of itself; it re-derives the answer from the code.

Assign this as a **new Jules session pointed at the branch behind the Implement Missing Features PR — not `main`.** That branch is the only place where both report files and the actual changed code exist together before merge, which also makes this a natural pre-merge gate: run it, get a verdict, then decide whether to merge.

## Prompt

```markdown
# Missing Features Verification Audit (Jules) — Prompt

Assign this to Jules as a new session against the implementation branch/PR you want verified. Paste everything below as the task description.

---

You are acting as a senior engineer doing a **reconciliation audit**: checking whether a claimed implementation actually closed the gaps identified in an earlier audit. Your only output is a markdown report (and, where possible, a PR comment). Do not modify any source file, and do not fix anything you find wrong — this is a read-only pass.

## Step 0 — Locate both inputs and confirm you're on the right branch

- Confirm your cloned snapshot is the branch/PR produced by the Implement Missing Features session, not `main`. If you were assigned against `main` and the relevant branch hasn't merged yet, stop and report that this session needs to be re-pointed at the implementation branch.
- Read `/doc/missing-features-<date>.md` (the original audit) and `/doc/implemented-features-<date>.md` (the implementation report) from your cloned snapshot. If either is missing, stop and name which upstream step — the Audit or the Implement session — needs to run first. Do not try to reconstruct a missing report from git history yourself.
- If multiple dated files of either type exist, use the implementation report's own "Source report" field to identify the correct audit report to pair it with, rather than assuming the newest file of each type is the matching pair.

## Step 1 — Build the full checklist from the original audit

Extract every row from the original report's Explicit Gaps and Inferred Gaps tables into one master checklist. This defines the complete scope this pass is responsible for. Do not drop an item just because the implementation report never mentions it — an item the implementer never addressed at all is itself a finding (see Step 4).

## Step 2 — Independently verify every "Implemented" claim against the code

The implementation report is a claim, not evidence. For each row in its Implemented table:
- Open the listed files and confirm the feature actually exists and does what the original gap described — not just that something changed in that area.
- Confirm it handles failure paths (network errors, empty/invalid input, permission denials), not only the happy path, unless the original gap was purely cosmetic.
- Confirm it matches the surrounding codebase's conventions (naming, structure, error-handling pattern) rather than introducing a one-off style.
- Confirm tests were actually added where claimed, and that they exercise real behavior rather than trivially passing.
- Search the "implemented" code specifically for any new `TODO`, `FIXME`, `NotImplementedException`, or stub pattern. A leftover stub means the item is not actually done, regardless of what the report claims.

## Step 3 — Check every "Skipped or Deferred" item for a legitimate reason

- For items skipped as "needs product decision," check whether anything in the codebase or docs has resolved that since.
- For items skipped as "disagreed with inference," independently re-examine the original evidence yourself and state whether you agree with the implementer's disagreement.
- Flag any skip that reads like scope-avoidance rather than a real blocker — e.g., a stated reason that doesn't match the actual complexity of the item.

## Step 4 — Check for anything the implementation report doesn't mention at all

Cross-reference the Step 1 master checklist against both the Implemented and Skipped/Deferred tables. Anything from the original audit that appears in neither is an **unreported gap** — the implementer either missed it or silently dropped it. This is a distinct, higher-concern category than an openly acknowledged skip, and should be reported as such.

## Step 5 — Check for regressions

- Review the diff between this branch and its base branch, not just the files the implementation report lists, for changes outside the reported scope.
- For any existing feature touched incidentally, confirm it still behaves as it did before. Fixing gap A while quietly breaking working feature B is a regression — report it regardless of how minor it looks.
- Re-run the project's lint/typecheck/test commands yourself in this session rather than trusting that the implementation session's own verification pass was accurate.

## Step 6 — Classify every item and generate the report

Assign each item from the Step 1 checklist exactly one status:
- **Verified Complete** — implemented, matches original intent, meets the codebase's existing quality bar, tested.
- **Implemented but Incomplete** — code exists but fails part of Step 2 (missing failure-path handling, no tests, style mismatch, leftover stub).
- **Claimed Complete but Not Found** — the implementation report says done; you could not verify it in the code.
- **Legitimately Deferred** — skip reason checked out in Step 3.
- **Deferred Without Sufficient Reason** — skip reason didn't hold up.
- **Unreported Gap** — absent from both tables in the implementation report (Step 4).
- **Regression Introduced** — new problem in previously-working code (Step 5); list even if it doesn't map to an original gap row.

Write the output to `/doc/verification-<YYYY-MM-DD>.md`:

```markdown
# Missing Features Verification Audit — [Project Name]
Generated: [date]
Missing-features report audited: [path]
Implementation report audited: [path]
Branch/PR verified against: [branch name or PR link]

## Summary
[3-5 sentences: overall completion rate, whether this PR looks safe to merge as-is, and the single biggest concern if any]

## Verified Complete
| Feature | Evidence |
|---|---|

## Implemented but Incomplete
| Feature | What's missing from the implementation | Original location |
|---|---|---|

## Claimed Complete but Not Found
| Feature | What the implementation report claimed | What you found instead |
|---|---|---|

## Deferred — Legitimate
| Feature | Reason (validated) |
|---|---|

## Deferred — Without Sufficient Reason
| Feature | Stated reason | Why it doesn't hold up |
|---|---|---|

## Unreported Gaps
| Feature | Original location | Notes |
|---|---|---|

## Regressions Introduced
| What broke | Location | Caused by |
|---|---|---|

## Merge Recommendation
[Ready to merge as-is / merge with follow-up items filed / do not merge — reasons]

## Open Questions for the Team
[Anything genuinely ambiguous requiring a human call, not a guess]
```

## Rules
- Read-only pass: do not fix, implement, or modify anything during this session, including regressions you find. Report them; a fix belongs in a new Implement Missing Features session.
- Never accept the implementation report's own claim as sufficient evidence — every "Implemented" row must be independently re-checked against the code before being marked Verified Complete.
- Cite exact file paths and line numbers/function names for every finding, the same bar as the original audit.
- If you cannot access the implementation branch (only `main` is available and it's already merged), say so explicitly and verify against `main` instead, noting that pre-merge regressions could already be masked by the merge commit.
- Deliver the report both as the committed `/doc/verification-<date>.md` file and as a comment on the implementation PR if this session has PR-comment capability, so a reviewer sees the verdict without opening a second file.
- If the Step 1 master checklist and the two tables in the implementation report don't reconcile cleanly, say so explicitly rather than silently making them appear consistent.
```
