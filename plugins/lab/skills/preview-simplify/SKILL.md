---
name: preview-simplify
description: >-
  Use when you want concrete simplification suggestions for recently changed code — clarity,
  nesting, naming, dead abstractions, magic values — reported as a proposal without touching
  any file. Triggers on "simplify preview", "what could be simplified", "suggest simplifications".
argument-hint: "[paths or scope; default: recently modified code]"
disable-model-invocation: true
user-invocable: true
disallowed-tools: [Write, Edit]
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# Preview Simplify

Propose refinements that make recently modified code clearer, more consistent and more maintainable
while preserving exact functionality. Prefer readable, explicit code over overly compact solutions.

Report the proposal only. **Do not modify any file** — the output is a list of suggested changes,
not the changes themselves.

## Rules

Apply the `clean-code` rules. If they are not already loaded in context, look for
`clean-code.md` under `.claude/rules/` — in the project or under `$HOME` — and read it.

## Scope

`$ARGUMENTS` may name files, directories or a scope to analyze. When omitted, analyze only code that
was modified recently or touched in the current session — do not widen the scope on your own.

## What to apply

1. **Preserve functionality** — never change what the code does, only how it does it. All original
   features, outputs and behaviors must remain intact.
2. **Apply language idioms and project conventions** — use idiomatic patterns for the language at
   hand and follow the project's established naming, formatting and structural conventions. When the
   project includes language-specific style rules, apply them.
3. **Enhance clarity** — simplify code structure by:
   - Reducing unnecessary complexity and nesting (max 2–3 levels)
   - Using guard clauses and early returns to avoid deep indentation
   - Eliminating redundant code and abstractions
   - Improving readability through clear, intent-revealing names
   - Replacing boolean flag arguments with enums or separate methods
   - Replacing magic numbers and strings with named constants or enums
   - Following Command-Query Separation: queries must not change state
   - Removing comments that just restate what the code does — keep only those explaining WHY
   - Choosing clarity over brevity — explicit code is better than overly compact code
4. **Maintain balance** — avoid over-simplification that would:
   - Reduce code clarity or maintainability
   - Create clever solutions that are hard to understand
   - Combine too many concerns into a single method or class
   - Remove helpful abstractions that improve code organization
   - Prioritize "fewer lines" over readability
   - Make the code harder to debug or extend

## Procedure

1. Identify the code sections in scope.
2. Analyze them for opportunities to improve clarity and consistency.
3. Apply the rules above and the project's own conventions.
4. Report each finding with a file reference and line link (`[file.ts:42](file.ts#L42)`), what to
   change and why, and the concrete better variant. If nothing is worth changing, say so.
