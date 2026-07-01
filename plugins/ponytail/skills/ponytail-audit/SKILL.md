---
name: ponytail-audit
description: >
  Audit the whole repo (or a given path) for over-engineering and hand back
  a ranked delete-list. Runs only when the user explicitly invokes it.
disable-model-invocation: true
user-invocable: true
argument-hint: "[path]"
origin: https://github.com/DietrichGebert/ponytail
license: MIT
---

# Ponytail Audit

Scan $ARGUMENTS for over-engineering only — not correctness, not bugs. Default
to the whole repo when no path is given; scan the tree, not a diff. Report
only — change nothing.

One line per finding, ranked biggest cut first:

`<tag> <what to cut>. <replacement>. [path]`

Tags (mirror the ponytail ladder):

- `delete` — dead code or speculative feature
- `stdlib` — reinvented standard library
- `native` — dependency doing what the platform already does
- `yagni` — abstraction with one implementation
- `shrink` — same logic, fewer lines

Skip anything already marked with a deliberate `ponytail:` comment — its
ceiling and upgrade path are on record.

End with the net removable lines and dependencies. If nothing to cut:
`Lean already. Ship.`
