---
name: final-review
description: >-
  Review a finished implementation against its plan — a fresh subagent, briefed only on what you
  give it, hunts regressions in behavior that had to stay and bugs in the new code.
argument-hint: "[plan.md] [staged|branch|last|A..B|paths]"
disable-model-invocation: true
user-invocable: true
allowed-tools:
  - Agent
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(git merge-base:*)
  - Bash(git symbolic-ref:*)
  - Read
  - Glob
  - Grep
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-09-09 09:35:47"
---

# Final review

Run this once a plan has been implemented. You carry the whole session; the reviewer carries nothing.
Whatever you leave out of the brief is what nobody will check.

**Write the report in the language the user speaks in this conversation.** The bracket labels stay in
English — they are identifiers, not prose.

## Procedure

1. **Resolve the inputs.** Read `$ARGUMENTS` in this order: a path ending in `.md` is the plan; then
   the keywords `staged` / `branch` / `last`; then a range containing `..`; then existing file paths;
   anything left over is ignored.
   - **Plan** — the plan the implementation followed. Never guess it and never search for candidates:
     with no path given, ask for one. Only once the user confirms there is no plan do you write
     section 1 of the brief from the session, and the brief says that is where it came from.
   - **Scope** — with no scope given, review the working tree: `git status --porcelain` for the paths,
     including untracked ones, and `git diff` for the tracked content. Only when the working tree is
     clean fall back to the branch diff against the default branch (`git merge-base`).
   - `git diff` never shows an untracked file. Read every new file in the scope in full and carry it
     into the brief as added — a change that only adds files is otherwise reviewed as if it were empty.
   - If the resolved scope is empty, say so and stop. Never write a brief for an empty diff.
2. **Enumerate the frozen behavior mechanically.** Never from memory — memory is what produced the
   change you are about to have reviewed:
   - `git diff` over the scope for the public signatures: symbols added, removed, changed. For a new
     file the whole file is the addition.
   - `Grep` for the callers of every changed public symbol.
   - `Glob`/`Grep` for the tests covering the affected code.
   - From the diff itself: side effects, call order, return values, eager vs. lazy evaluation.
3. **Write the brief** — the five sections below — and print it. The user has to see what the reviewer
   was given.
4. **Run the reviewer.** One subagent, the brief plus the inputs below. It reports only; it must not
   edit a file.
5. **Verify the findings.** Take a skeptical second pass over each one against the actual code. Drop
   what you cannot confirm; phrase what you are unsure of as a question, not an assertion.
6. **Print the report.**

## The brief

1. **Goal** — one or two sentences: what the change was meant to achieve, and what was explicitly
   *not* a goal.
2. **Closed decisions** — a list: decision plus a one-line rationale. Include the deviations from the
   plan made during implementation, and why. If you did not implement the change yourself — a fresh
   session, someone else's work — derive this from the plan and from the commit messages in scope
   (`git log`), and say in the brief where it came from. Never invent a rationale.
3. **Frozen behavior** — the externally observable behavior that must not change, as enumerated in
   step 2. Not a prose summary: the signature diff, the covering tests, the side effects, call order,
   return values and evaluation timing.
4. **Instructions for the reviewer:**
   - Primarily look for regressions against section 3 and for bugs in newly written code.
   - Specifically check boundary behavior, error paths and exceptions, call order and idempotence,
     empty and null inputs, disposal, transactions, thread safety, and changes to eager vs. lazy
     evaluation.
   - Naming, structure and "this could be nicer" are suggestions, not defects.
   - Do not reopen section 2. If a decision there contradicts section 3 or the attached plan,
     report it as `[spec-conflict]`.
   - Report only — never edit a file.
5. **Output** — the report format below, handed over verbatim.

## Reviewer inputs

Attach alongside the brief:

- the plan verbatim, as a separate block — never paraphrased
- the full diff
- the callers of every changed public symbol
- the affected tests

Anything in section 3 the brief does not carry, the reviewer looks up in the repo itself; whatever it
cannot resolve it reports as `[unverifiable]`.

## Report format

One list of findings, each labelled `[regression]`, `[bug]`, `[spec-conflict]`, `[suggestion]` or
`[unverifiable]`, with a clickable reference `[path/to/file.ext:42](path/to/file.ext#L42)` and one
sentence saying why it matters. Quotes from the plan are copied verbatim — never corrected, never
translated.

Close with two or three bullets on what was actually checked, then a one-line count per label.

An empty findings list is a valid answer. Do not invent findings.
