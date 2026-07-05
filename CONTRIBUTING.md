# Contributing to AI Prompts Collection

Thank you for your interest in contributing! This repository aims to be a well-organized and high-quality collection of AI prompts.

## Folder Structure

Please place your prompts in the appropriate category folder:

- `coding/`: Prompts for software development, debugging, and implementation.
- `documentation/`: Prompts for generating technical docs, mapping codebases, or explaining logic.
- `review/`: Prompts for audits, security reviews, UI/UX passes, and architectural analysis.

If your prompt doesn't fit these, feel free to suggest a new category in your PR.

## File Naming Convention

- Use `lowercase-kebab-case.md` (e.g., `feature-audit-agent.md`).
- Always use the `.md` extension.

## Required Front Matter

Every prompt file must start with YAML front matter:

```yaml
---
title: "Descriptive Title"
description: "A one-sentence summary of what this prompt does."
category: "coding" # coding, documentation, or review
tags: [tag1, tag2]
compatible_models: [Claude, GPT-4, any]
author: "Your Name or GitHub Username"
added: "YYYY-MM-DD"
---
```

## Prompt Template

Use the following template for the file content:

```markdown
# [Prompt Title]

[Brief introduction or context for the prompt.]

## Prompt

```markdown
[Paste the actual prompt text here]
\```
```

## Quality Bar

To ensure the collection remains useful:
- **Tested**: The prompt should be tested with at least one major model (Claude, GPT-4, etc.).
- **Clear**: Provide clear instructions and avoid ambiguity.
- **Non-Duplicative**: Check if a similar prompt already exists.
- **Privacy**: Ensure no personal or sensitive data is included in the prompt.

## PR Process

1. **Fork** the repository.
2. **Create a branch** for your prompt (`git checkout -b add-my-awesome-prompt`).
3. **Add your file** following the standards above.
4. **Run the index builder** (optional but helpful): `python scripts/build_index.py`.
5. **Submit a PR**. One prompt per PR is preferred.

Happy prompting!
