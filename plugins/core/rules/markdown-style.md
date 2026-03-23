---
paths:
  - "**/*.md"
---

# Markdown Style Guide

Formatting (blank lines, trailing whitespace, heading style, list markers) is auto-fixed by the `.claude/hooks/fix-markdown.ps1` PostToolUse hook. Do not run the linter manually.

Focus on these rules that the auto-fixer cannot enforce:

- Use asterisks for emphasis: `*italic*`, `**bold**`. Never underscores.
- Use fenced code blocks (triple backticks) with a language identifier. Never indented code blocks.
- Prefer inline links `[text](url)` over reference-style links.
- Use code formatting (backticks) for file names, paths, commands, identifiers, and values.
- Use real numbering in ordered lists (1. 2. 3.), not all ones.
- Do not skip heading levels (e.g., `##` followed by `####`).
- Duplicate headings are allowed only among siblings (e.g., repeated `## Example` under different parents is OK).
- Inline HTML is allowed for legitimate cases (C# generics like `<T>`, complex tables). Avoid it otherwise.
- Be concise — prefer short paragraphs and bullet points over long prose.
