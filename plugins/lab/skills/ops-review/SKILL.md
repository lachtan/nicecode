---
name: ops-review
description: >-
  Use when reviewing an infrastructure or ops change — IaC, config management, container or
  deployment manifests, CI pipelines, ops scripts — for intent-fit, logic, idempotency, needless
  complexity, file organisation and readability: the problems linters and formatters do not catch.
argument-hint: "[paths, HEAD, or --staged]"
disable-model-invocation: true
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-08-27 05:55:11"
---

# Ops Review

Review an infrastructure or ops change for **intent, logic, idempotency, idiomaticity, simplicity,
readability and cross-file integrity** — the problems the repo's linters and formatters do **not**
catch. High signal only.

## 1. Scope

Determine what to review from the argument (`$ARGUMENTS`):

- **No argument (default):** changed files vs the repo's default branch —
  `git diff --name-only $(git merge-base HEAD <default-branch>)...HEAD`, plus uncommitted changes
  (`git status --porcelain`).
- **Paths / component names:** review only those files/directories.
- **`HEAD` or "last commit":** `git show --name-only HEAD`.
- **`--staged`:** `git diff --cached --name-only`.

If there are no relevant changes, say so and stop.

## 2. Intent

Before reviewing, work out **what the change is trying to achieve** and state it in 1–2 sentences:

- Sources: commit messages (`git log <default-branch>..HEAD --oneline`), the PR/MR description via
  whatever CLI the repo uses (`gh pr view`, `glab mr view`), and the diff itself.
- If the goal is genuinely unclear, **ask the user** — do not guess.

Pass this intent summary to **every** review agent as the lens they judge findings against.

## 3. Context

Read project conventions only to understand intent — **never** re-flag style: `CLAUDE.md` and
`.claude/rules/` that apply to the changed files, plus the surrounding files to infer the repo's own
idioms. Respect those idioms so suggestions don't fight existing conventions.

**Ground idiomaticity claims in docs, not memory:** before calling a tool or module misused or
non-idiomatic, verify against its official documentation (WebFetch) or its built-in help
(`--help`, `man`, the tool's own doc command). No claims from memory.

## 4. Review (parallel agents)

Launch agents in parallel (single message). Give each the diff, the changed file list and the intent
summary from §2. Each returns findings, each with `file:line`, a **severity** (blocker /
recommendation / nit), a short description, and the reason it was flagged. For simplicity and
readability findings, include a **concrete better alternative**, not just the problem.

- **Goal-fit (intent)** — does the change actually achieve the stated goal? Missing step toward the
  goal, steps that won't produce the intended effect, half-finished implementation, a forgotten
  restart / reload / hook the change relies on to take effect.
- **Idempotency & re-runnability** — steps that fail or overwrite on a second run; an imperative
  command where a declarative mechanism does the same job; a missing guard ("only do this when …");
  destructive or non-reentrant operations.
- **Logic & correctness** — broken conditions, loops and templating; variable precedence and
  overrides; references to undefined variables or values; wrong privilege or context scope.
- **Idiomaticity & simplicity** — a hand-rolled script where the tool has a native mechanism; a
  non-canonical pattern (verified against docs); redundant or duplicate steps; needlessly complex
  conditions, loops or filters; premature generalisation. Find what can be **simplified and made
  idiomatic** — with the better variant — not style.
- **File organisation** — is the change split sensibly? A bloated entry file that should move into
  included sub-files; conversely trivial over-splitting; a step that belongs elsewhere (a hook vs. a
  regular step, a value that belongs in configuration vs. inline).
- **Readability & clarity** — unclear step / variable / function names, magic values without
  explanation, unclear purpose of a step, a missing comment on non-trivial logic, tangled structure.
  Always include a suggested improvement.
- **Cross-file integrity & ordering** — do referenced variables, templates, files, modules and hooks
  exist? Sensible ordering and dependencies between steps; impact on the production environment the
  change targets.
- **Script bugs** — real defects in any embedded or accompanying scripts (shell, Python, …): broken
  control flow, unhandled error states, fragile assumptions. Behaviour, not style.

Security (plaintext secrets, dangerous commands) is **low priority** — not the focus. Mention only if
a finding is obvious and serious.

## 5. Validate

For each finding, do a skeptical second pass: confirm it is real with high confidence against the
actual code. **Do not call something a bug or redundancy unless certain — if unsure, phrase it as a
question.** Drop unconfirmed findings. A proposed fix must also be **behavior-preserving**: trace
every piece of state it changes (exit codes, change/notify signals, outputs consumed downstream),
since a break can land in a *different* step than the one edited.

## 6. Output

Group by file, high signal only. Lead each finding with its severity. For simplicity and readability
findings, show the concrete better variant.

Do **not** report: style, naming conventions, formatting, or anything the repo's linters and
formatters already catch; pre-existing issues outside the diff; pedantic nitpicks.

If nothing found, say so and name what was checked: logic, idempotency, integrity, idiomaticity,
complexity, organisation, readability and intent-fit.
