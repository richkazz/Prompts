# Missing & Incomplete Features Audit — Prompt

Copy everything below into your coding agent (Claude Code, Cursor, etc.) at the root of the project.

---

You are acting as a senior engineer doing a **gap analysis** on an existing codebase: finding what's missing, half-built, or was clearly intended but never finished. Your only output is a markdown report. Do not modify any source file, including TODO comments.

## Step 1 — Establish what "complete" looks like for this project

Before hunting for gaps, build a picture of the intended feature set from every available signal:
- README, design docs, `/doc` folder, changelogs, or spec files
- Route/navigation definitions (a route or nav entry implies a destination should exist)
- UI elements that exist but do nothing yet (buttons, icons, menu items wired to empty handlers or `print`/`console.log` stubs)
- Model/schema fields that are defined but never read or written anywhere
- Named-but-empty functions, classes, or files (e.g. `AuthService.resetPassword()` with a stub body)
- Package/dependency list — is anything installed but never actually used, suggesting a feature was started and abandoned?
- Commit messages or PR titles if git history is available (`git log --oneline`) — look for "WIP," "part 1," "TODO," reverted commits, or commits that add a stub without a follow-up

If there's no explicit spec, say so and note that intended scope is being inferred entirely from code signals.

## Step 2 — Direct evidence of incompleteness

Search systematically for explicit markers first — these are the highest-confidence findings:
- `TODO`, `FIXME`, `HACK`, `XXX`, `NOTE:` comments — quote them and their location
- `throw UnimplementedError`, `NotImplementedException`, `pass  # placeholder`, `// coming soon`, or equivalent stubs in the language in use
- Disabled/commented-out code blocks left in place (may indicate an abandoned attempt, not just dead code)
- Feature flags that are permanently off, or config toggles with no corresponding working feature
- Hardcoded placeholder data, mock responses, or `TODO: replace with real API` patterns
- Empty catch blocks or error handlers that silently swallow errors where a real handling path was clearly intended

## Step 3 — Inferred gaps (no explicit marker, but strongly implied)

This is the harder, more valuable part. Look for **structural evidence that something was meant to exist** even without a comment saying so:
- A UI element with no visible destination (e.g. a settings icon with no settings screen; a "share" button with no share logic)
- A model/database field that exists in the schema but is never populated or displayed anywhere in the UI
- An API endpoint or service method defined but never called from any screen
- Asymmetric CRUD — e.g. create and read exist, but update or delete are missing for the same entity
- A permission/auth check for a role or state that's never actually reachable in the app (e.g. an `isAdmin` check with no way to become an admin)
- Two parallel implementations of similar logic where one looks newer/incomplete — infer which was meant to replace the other
- Localization/i18n scaffolding present but only one language ever populated
- Tests written for functionality that doesn't exist yet (tests can reveal intended behavior even before the code catches up), or the reverse — functionality with zero test coverage in an otherwise well-tested codebase

For every inferred gap, explicitly state **why you believe it was intended** (cite the specific evidence — file, field, naming, or pattern) and rate your confidence: **High / Medium / Low**. Never present an inference as a confirmed fact.

## Step 4 — Classify each finding

For every gap found (Step 2 or 3), record:
- **Feature/area name**
- **Evidence type:** Explicit marker / Inferred
- **Confidence** (for inferred items): High / Medium / Low
- **Location(s):** exact file paths, line numbers, function/component names
- **What appears to be missing:** plain description
- **What it would take to finish:** rough scope — is this a small stub-fill, or does it imply new screens/services/data model changes?
- **User impact if left unfinished:** does this block a core flow, degrade an edge case, or is it cosmetic?

## Step 5 — Generate the report

Write the output to `/doc/missing-features-<YYYY-MM-DD>.md` (create `/doc` if it doesn't exist). Use this structure:

```markdown
# Missing & Incomplete Features Audit — [Project Name]
Generated: [date]
Spec source: [documented spec found at X / inferred entirely from code]

## Summary
[3-5 sentences: how many explicit vs inferred gaps found, and the biggest theme — e.g. "auth flows are mostly stubbed," "AI features are ahead of core CRUD," etc.]

## Explicit Gaps (marked in code)
| Feature | Location | Marker/Evidence | What's missing | Impact |
|---|---|---|---|---|

## Inferred Gaps (not marked, but implied by structure)
| Feature | Location | Evidence for inference | Confidence | What's missing | Impact |
|---|---|---|---|---|---|

## Asymmetric/Partial Implementations
[Cases where some but not all of an expected set exists — e.g. Create+Read but no Update/Delete]

## Abandoned or Duplicate Attempts
[Parallel implementations, dead branches of logic, or stubs that suggest a restart mid-feature]

## Recommended Priority Order
[Ordered list: which gaps most likely block real usage vs. which are edge cases or polish, and why]

## Open Questions for the Team
[Anything genuinely ambiguous that needs a human decision, not a guess — e.g. "was X intentionally descoped, or just not finished?"]
```

## Rules
- Every finding must cite an exact file path (and line number or function name where possible) — no vague claims like "auth seems incomplete somewhere."
- Keep explicit and inferred findings clearly separated — never blend a confirmed TODO with a guess in the same confidence tier.
- Do not fix, implement, or stub anything during this pass. Output is the report only.
- If the codebase is large, prioritize core user flows (auth, primary CRUD, primary AI/business logic) before secondary or admin-only areas, and note explicitly what was out of scope for this pass.
