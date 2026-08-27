---
name: quick-review
description: >-
  Use when reviewing changed code for correctness, security and clean-code violations — a single
  fast pass over staged changes, a branch diff, the last commit, a commit range or given paths,
  with an optional focus area (security, error handling, performance).
argument-hint: "[staged|branch|last|A..B|paths] [focus]"
disable-model-invocation: true
user-invocable: true
disallowed-tools: [Write, Edit]
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-08-27 05:54:13"
---

# Quick Review

Review code changes by applying the clean-code rules. Do not invent your own checklist — the rules
define what to check. Review only the changed code — do not suggest refactoring or style fixes for
unchanged surrounding code.

Report findings only. **Do not modify any file** — no fixes, no formatting, no cleanup.

## Rules

Apply the `clean-code` rules. If they are not already loaded in context, look for
`clean-code.md` under `.claude/rules/` — in the project or under `$HOME` — and read it.

## Arguments

`$ARGUMENTS` contains two optional parts in any order:

- **Scope** — what code to review: `staged`, `branch`, `last`, a commit range with `..` (e.g.
  `HEAD~3..HEAD`), or file paths. When omitted, review staged changes if any exist, otherwise the
  full branch diff.
- **Focus** — everything else is treated as a free-text focus area (e.g. `security`,
  `error handling`, `performance`). When specified, prioritize findings in that area but still
  report any critical issues outside it.

Detection order: keywords (`staged`, `branch`, `last`) → `..` (range) → existing file paths →
remaining text is focus.

## Always Check

Beyond the clean-code rules, always check for:

- **Security** — injection (SQL, XSS, command), hardcoded secrets, unvalidated input, path
  traversal, sensitive data exposure, authentication/authorization flaws.
- **Correctness** — logic errors, race conditions, null/undefined handling, off-by-one, unhandled
  edge cases, infinite loops.
- **Error handling** — swallowed exceptions, lost error context, missing error propagation.

## Procedure

1. **Get diff** — detect base branch, run the appropriate `git diff` and `git log --oneline`. If the
   diff is empty, write "No changes to review" and stop.
2. **Read context** — for each changed file, read relevant sections. Also read unchanged files that
   provide important context (base classes, interfaces, called methods).
3. **Analyze** — use commit messages and context to understand the intent behind each change. Then
   evaluate whether the code correctly achieves that intent AND whether it violates the rules.
   Classify each finding as **Critical** (must fix), **Important** (should fix), or **Minor**
   (nice to fix) based on impact. Skip pure stylistic issues that formatters handle. Be thorough —
   missing a real bug is worse than being strict.
4. **Report** — output findings grouped by severity (critical first). For each finding:
   - File reference with line link: `[file.ts:42](file.ts#L42)`
   - What the issue is and why it matters
   - A concrete fix (code or clear instruction, not just criticism)

   End with a one-line summary of total findings by severity. If no issues found, write
   "No issues found."
