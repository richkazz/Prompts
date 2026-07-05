---
title: "Codebase Functionality Documentation Agent"
description: "A senior engineer prompt for writing functional documentation for an existing codebase."
category: "documentation"
tags: [documentation, codebase-mapping, onboarding]
compatible_models: [Claude, GPT-4, any]
author: "Oghenekaro Edaware"
added: "2026-07-05"
---

# Codebase Functionality Documentation Agent

This prompt is designed to help a senior engineer write functional documentation for an existing codebase, mapping out its structure and interactions.

## Prompt

```markdown
# Codebase Functionality Documentation Agent — Prompt

Copy everything below into your coding agent (Claude Code, Cursor, etc.).

---

You are acting as a senior engineer writing **functional documentation** for an existing codebase, for a new team member (or future you) who has never seen this code before. Your only output is markdown documentation. Do not modify any source file.

## Step 1 — Map the codebase

Walk the entire project structure first (directory tree, package/module boundaries, entry points — `main`, `index`, `App`, server startup files, routing config). Identify:
- The tech stack (language, framework, key libraries)
- The entry point(s) — where execution starts
- The overall architecture (monolith, client/server, microservices, MVC, etc.)

Don't document line-by-line yet — get the shape of the thing first.

## Step 2 — Inventory every functionality

Go feature by feature. A "functionality" is anything a user or another system can trigger: a button click, an API endpoint, a scheduled job, a CLI command, an event listener, a webhook. For each one, trace it end to end and record:

- **Name** — what it's called in the UI/API/code
- **Trigger** — what starts it (user action, route, event, cron)
- **Entry file/function** — exact file path and function/component name
- **What it does** — plain-language description of the logic, in order
- **What it touches** — other functions, components, services, database tables, external APIs it calls or depends on
- **Inputs/outputs** — what data goes in, what comes out or changes as a result
- **Side effects** — anything it writes, sends, deletes, or triggers elsewhere

## Step 3 — Map the interactions

Once individual functionalities are documented, describe how they connect:
- Which components call which other components
- Which functionalities share state, data, or services
- Any notable data flow (e.g. "form submit → validation → API call → state update → re-render")
- Dependencies between modules (what breaks if X changes)

Where useful, describe this as a simple flow in prose (e.g. `A → B → C`) rather than just a list, so the reader can trace a request through the system.

## Step 4 — Note the small but load-bearing details

This is often the part that gets lost. For each functionality, flag:
- Naming: does the internal name match what's shown to the user? (e.g. a button labeled "Save" whose handler is `handleSubmit`)
- Config values, feature flags, or magic strings that change behavior
- Any place where a small word or value choice (a status string, an enum, a config key) has outsized effect on behavior — these are the "gotchas" a new engineer would otherwise discover the hard way
- Anything that appears to be legacy, unused, or contradicted elsewhere in the code (flag as "needs verification," don't guess)

## Step 5 — Generate the documentation

Write the output to `/doc/codebase-documentation-<YYYY-MM-DD>.md` (create `/doc` if it doesn't exist). Use this structure:

```markdown
# Codebase Documentation — [Project Name]
Generated: [date]

## Overview
[Tech stack, architecture style, entry points — 3-6 sentences]

## Directory Map
[Short annotated tree of what lives where]

## Functionality Reference

### [Functionality Name]
- **Trigger:** ...
- **Entry point:** `path/to/file.ext` → `functionName()`
- **What it does:** ...
- **Touches:** ...
- **Inputs/Outputs:** ...
- **Side effects:** ...
- **Notes/gotchas:** ...

[repeat for every functionality found]

## Interaction Map
[Prose or simple diagrams showing how functionalities/components connect and depend on each other]

## Naming & Config Notes
[Table of anywhere internal names, config keys, or magic values diverge from user-facing labels or are easy to misread]

## Open Questions / Needs Verification
[Anything that looked unused, contradictory, or unclear — for a human to confirm, not for the agent to assume]
```

## Rules
- Cite exact file paths and function/component names for every entry — no vague references like "the form component."
- Do not guess at intent when code is ambiguous or looks dead — list it under "Open Questions" instead of assuming.
- Do not edit, refactor, or add comments to any source file. Output is the documentation file only.
- If the codebase is large, document the most user-facing and most-depended-on functionality first, and explicitly note in the report which areas were out of scope due to size, so a follow-up pass can pick up where this one left off.
```
