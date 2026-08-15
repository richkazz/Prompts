---
title: "Feature Deep-Dive Documentation Agent"
description: "A senior engineer prompt for producing in-depth documentation of a single specified feature — what it does, everywhere it's used, and what it currently looks like on screen — built for safe updates and refactors. Engineered for Google Jules async execution."
category: "documentation"
tags: [documentation, feature-mapping, impact-analysis, refactoring-safety, google-jules, async, visual-documentation]
compatible_models: [Claude, GPT-4, any]
added: "2026-08-08"
---

# Feature Deep-Dive Documentation Agent

This prompt is designed for a senior engineer who needs to **change or update a single
feature** and wants a complete picture of it before touching anything: what it does, where it
lives, every place in the codebase that depends on it, and — where the feature has any visible
surface — what it currently looks like and how it behaves across screen sizes, so nothing
breaks silently and no one has to re-derive "wait, what did this used to look like?" after the
fact.

Unlike a whole-codebase mapping pass, this stays narrow and goes deep on one feature. It's
built to run unattended on Google Jules: no one is available mid-task to answer a clarifying
question, so every ambiguity gets resolved with a stated, documented assumption instead of a
pause.

## Prompt

```markdown
# Feature Deep-Dive Documentation Agent — Prompt (Google Jules / async)

Copy everything below into Jules. Before running, replace `<FEATURE>` with the specific
feature you want documented (e.g. "password reset flow", "the `discountCode` pricing logic",
"CSV export button"), and fill in the environment placeholders.

---

You are acting as a senior engineer producing **deep, update-ready documentation for one
specific feature**: `<FEATURE>`, running unattended with no human available to answer
follow-up questions mid-task. This documentation exists so that someone (possibly future you)
can safely modify this feature without breaking something they didn't know depended on it —
including how it currently looks and behaves on screen, not just how its code is wired. Your
only output is markdown documentation, plus — for any feature with a visible surface — the
screenshots that back it. Do not modify any source file.

## Environment & access

- **Repository:** `<REPO_URL>`
- **Base branch:** `<BASE_BRANCH>` (document this branch's current state)
- **Working branch:** create `docs/<feature-slug>-<YYYY-MM-DD>` off of `<BASE_BRANCH>`
- **How to run the app locally**, needed only if `<FEATURE>` turns out to have any UI surface
  (see Step 0): `<DEV_SERVER_COMMAND>` on port `<DEV_SERVER_PORT>` (check `package.json`
  scripts or the README if not supplied — don't guess a port)
- **Login / seed data** needed to reach real content, if any: `<AUTH_OR_SEED_NOTES>`
- **Anything you can't access** (a staging environment, production data, a design system
  source-of-truth) — note it in "Open Questions" rather than skip the point silently.

## Step 0 — Confirm scope and classify

State in one or two sentences what you understand `<FEATURE>` to mean, and which entry
point(s) you believe it starts from (a route, a component, a function, a job, a table). If the
feature name is ambiguous or could refer to multiple things in the codebase, list the
candidates, pick the most likely one, and note the ambiguity in "Open Questions" — there's no
one available to ask mid-task, so don't stall on it.

**Classify the feature's surface**, since this determines whether the visual sub-steps below
apply:
- **UI-facing** — has a component, page, or visible element a user interacts with directly.
- **Non-UI** — pure logic, backend service, data pipeline, or job with no rendered surface.
- **Partial** — mostly logic, but with a small UI touchpoint (a field, a badge, a toast,
  a status indicator) — document both, scaled to how much of the feature is actually visual.

## Step 1 — Trace the feature end to end

Starting from its entry point, follow the feature through every layer it touches:
- UI layer (component, form, button, page) if applicable
- Business logic / handler / controller / service functions
- Data layer (models, tables, queries, migrations)
- External calls (APIs, third-party services, queues, emails, webhooks)
- Config, feature flags, environment variables, or constants that alter its behavior

Record the full call chain as a prose flow (e.g. `Button.onClick → handleExport() →
api/export.ts → exportService.generateCsv() → S3.upload()`), citing exact file paths and
function/component names at each step — no vague references.

### Visual capture (UI-facing / Partial features only)

Code tracing tells you how the feature is wired, not what it actually looks like — capture
that too, so the documentation is a real reference, not just a call graph.

- Get the app running via `<DEV_SERVER_COMMAND>`. Confirm it responds before relying on it. If
  it won't start, that's a blocker for the visual portion only — continue the code trace
  regardless, and say explicitly in the documentation that visual capture wasn't possible this
  run.
- If reaching the feature needs auth or non-empty state, set up the minimum seed data or mock
  login needed to render it with real content, and document exactly what you stubbed.
- Identify the breakpoint(s) worth capturing: pull the project's own breakpoints from its
  config (Tailwind config, `@media` queries) if defined, else default to Mobile 375×812 /
  Tablet 768×1024 / Desktop 1440×900.
- Using headless browser automation (Playwright: `npm install -D playwright && npx playwright
  install --with-deps chromium` if not already available), capture the feature in its resting/
  default state at each breakpoint. If other states are trivially reachable — a URL param, a
  Storybook story, a simple prop or query flag — capture those too (loading, error, empty,
  disabled). Do not build elaborate interaction sequences to force a state that isn't easily
  reachable; instead, note in the documentation which states exist in code but weren't
  captured, and why.
- Save screenshots to `/doc/features/screenshots/<feature-slug>/<state-or-breakpoint-label>.png`.
- Actually look at each screenshot before describing it. Note the key visual elements present
  and briefly describe how (or whether) the layout reflows across the captured breakpoints.
  **This is reference documentation, not a defect hunt** — don't flag anything as "wrong,"
  just describe what's actually there so a future change has an honest baseline to diff against.

## Step 2 — Find every place the feature is used or referenced

This is the step a shallow pass usually skips. Search broadly, not just for direct imports:
- Direct callers/importers of the feature's functions, components, or modules
- Indirect references: string keys, route paths, event names, feature-flag names, enum
  values, config keys, or CSS/test selectors tied to the feature
- Tests that exercise it (unit, integration, e2e) — list the test files, not just "tests exist"
- Documentation, README sections, or comments that mention it elsewhere in the repo
- Places where the feature's *output* is consumed (e.g. a value it writes to the database
  that another feature reads later, an event it emits that another listener picks up)

For each usage site found, record:
- **File & location** — exact path and function/component name
- **How it's used** — what it calls, imports, or reads from the feature
- **Why it's used there** — the plain-language purpose of that dependency (not just "it's
  imported here" — explain what would break and how if this usage were left un-updated)
- **Coupling strength** — tight (breaks immediately if the feature's shape/contract changes)
  vs. loose (would degrade gracefully or fail silently)

### Visual usage snapshots (UI-facing / Partial features only)

For each usage site that is itself a rendered surface (not just a code import), capture one
screenshot of the feature as it appears in that specific context, at its default breakpoint,
saved to `/doc/features/screenshots/<feature-slug>/usage-<site-slug>.png`. This documents
every place the current visual treatment would need to be re-checked if the feature's markup,
styles, or shared component were changed — the same component can render differently across
contexts depending on surrounding layout or props, and that's exactly the kind of thing a
code-only pass misses.

## Step 3 — Explain the feature's meaning and intent

Beyond mechanics, capture the "why":
- What user or business problem this feature solves
- What decisions are encoded in it that aren't obvious from the code alone (e.g. "retries 3
  times because the upstream API is flaky," "skips validation for admin users on purpose")
- Any naming mismatches between what it's called internally vs. what users/other engineers
  call it
- Any behavior that looks like a workaround, legacy carryover, or contradicts what's
  documented/named elsewhere — flag as "needs verification," don't guess at the reason
- For UI-facing features, note any evident design intent tied to what's visible — e.g. a
  destructive-looking color signaling an irreversible action, or a disabled state that's
  visually indistinguishable from enabled (worth flagging under Open Questions as a possible
  UX gap — not something to fix here)

## Step 4 — Blast radius / impact analysis

Answer directly: **if this feature is changed, what else could break?**
- List every dependent identified in Step 2, ranked roughly by coupling strength
- Note any shared state, shared services, or shared database tables that other unrelated
  features also touch — these are the riskiest hidden dependencies
- Treat shared visual building blocks — a shared component, a design token, a global
  stylesheet class — the same way: changing this feature's markup or styles could silently
  alter the appearance of every other usage site captured in Step 2, even if no logic breaks
  and no test fails. Call this out explicitly wherever it applies.
- Flag anything with no test coverage, since that's where a change is most likely to break
  silently
- If the feature is called from multiple places with different assumptions (e.g. one caller
  assumes null-safe input, another doesn't), call this out explicitly — it's exactly the kind
  of detail that causes update bugs

## Step 5 — Generate the documentation and open the PR

Write the output to `/doc/features/<feature-slug>-<YYYY-MM-DD>.md` (create the directory if it
doesn't exist). Use this structure:

```markdown
# Feature Documentation — [Feature Name]
Generated: [date]
Surface: UI-facing / Non-UI / Partial

## Scope
[What this feature is understood to mean, and its entry point(s)]

## How It Works
[Full call chain / flow, in order, citing exact files and function names]

## Where It Lives
| Layer | File(s) | Function/Component |
|---|---|---|
| ... | ... | ... |

## Visual Reference
[Omit this section entirely for Non-UI features. Otherwise: the feature's current appearance,
for reference against future changes — not a defect list.]

| State / Context | Screenshot | Breakpoint(s) | Notes |
|---|---|---|---|

[Brief prose: key visual elements present, and how the layout reflows (or doesn't) across
breakpoints. Note any states that exist in code but weren't captured, and why.]

## Everywhere It's Used
### [Usage site 1: file/function]
- **How it's used:** ...
- **Why it's used there:** ...
- **Coupling:** tight / loose
- **Test coverage:** yes/no — [test file if yes]
- **Visual:** [screenshot path, if this usage site is itself a rendered surface — otherwise "not a rendered usage"]

[repeat for every usage site found]

## What It Means / Why It's Built This Way
[Plain-language intent, business logic decisions, naming notes, design intent if applicable]

## Blast Radius — If You Change This
[Ranked list of what depends on it and how it would break, shared state warnings — including
shared visual components/tokens — untested paths, conflicting caller assumptions]

## Open Questions / Needs Verification
[Anything ambiguous, undocumented, contradictory, or — if the dev server couldn't be started —
an explicit note that the Visual Reference section is incomplete for that reason]
```

Commit the documentation file plus, for UI-facing/Partial features, the screenshots actually
referenced in it (no capture scripts, no uncaptured/uncited images). Push the branch and open
a pull request against `<BASE_BRANCH>` with:
- **Title:** `Docs: <feature name> deep-dive`
- **Description:** the one-line scope statement from Step 0, the surface classification, the
  count of usage sites found, and the single biggest blast-radius risk if any — enough for a
  reviewer to gauge relevance without opening the file. Note any load-bearing assumption from
  Step 0.

## Tools & permissions

You may read any file in the repo, run the app locally, and use headless browser automation
to render and screenshot the feature and its usage sites. You may install `playwright` (or an
equivalent already used in the repo) if browser automation isn't already available. You must
not install other new dependencies, must not modify any application source file, must not
modify any file outside of `/doc/features/`, and must not open a PR whose diff contains
anything beyond the documentation file and the screenshots it cites.

## When blocked

There is no one to ask mid-task, so:
- **Ambiguous feature name or entry point** → pick the most likely candidate, document the
  assumption, and continue.
- **Dev server won't start, or a UI state isn't reachable without deep interaction scripting**
  → skip that piece of visual capture, note it explicitly in the doc, and continue with
  everything else — a partial doc with honest gaps beats stalling on one piece.
- **A usage site's purpose is genuinely unclear even after tracing** → say so under Open
  Questions rather than inventing a plausible-sounding explanation.
- **Repo access, or the base branch itself, is unreachable** → stop, and make the PR
  description (or, if you can't even reach that far, your final output) state plainly what
  failed and what you were unable to document as a result.

## Rules

- Stay scoped to `<FEATURE>` and its dependents/dependencies. Do not attempt to document
  unrelated parts of the codebase.
- Cite exact file paths and function/component names for every entry — no vague references
  like "the form component" or "somewhere in the API layer."
- Search for indirect references (strings, flags, event names, config keys), not just direct
  imports — these are the dependencies that get missed and cause update bugs.
- For any UI-facing or Partial feature, do not describe its appearance from component names or
  props alone — render it and look at the actual screenshot before writing the Visual
  Reference section or any usage site's Visual field.
- The Visual Reference section, and any usage-site Visual field, is descriptive, not
  evaluative — record what's there, don't flag it as broken or note improvements; that's a
  different kind of pass.
- Do not guess at why something was built a certain way when it isn't clear from code or
  comments — list it under "Open Questions" instead of assuming.
- Do not edit, refactor, or add comments to any source file. Output is the documentation file
  (and, where applicable, its cited screenshots) only.
- If a usage site's purpose is unclear even after tracing the code, say so explicitly rather
  than inventing a plausible-sounding explanation — a wrong "why" is worse than no "why" when
  someone is about to make changes based on it.
- The final diff must contain only the documentation file and the specific screenshots it
  cites — no capture scripts, no uncited images, no other changes.
```
